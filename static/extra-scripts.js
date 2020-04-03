/**  
 * Note: Mostly borrowed from https://www.codexworld.com/export-html-table-data-to-csv-using-javascript/
 * This doesn't work very well at times but considering this isn't really for production, I'm not worrying 
 * about it too much Uses Windows line endings 
 */

/**
 * Download file
 * @param {String} fileContents String containing the file contents
 * @param {String} filename File name
 */
function downloadFile(fileContents, filename) {
    var generatedFile;
    var downloadLink;

    // CSV file
    generatedFile = new Blob([fileContents], {type: "text/csv"});

    // Download link
    downloadLink = document.createElement("a");

    // File name
    downloadLink.download = filename;

    // Create a link to the file
    downloadLink.href = window.URL.createObjectURL(generatedFile);

    // Hide download link
    downloadLink.style.display = "none";

    // Add the link to DOM
    document.body.appendChild(downloadLink);

    // Click download link TODO this might be blocked by certain browsers
    downloadLink.click();
}

/**
 * Generate CSV file with fields separated by commas and rows with \n Not very good
 * @param {String} filename File name
 */
function exportTableToCSV(filename) {
    var csv = [];
    // Get table rows
    var rows = document.querySelectorAll("table tr");
    // Iterate through the rows
    for (var row = 0; row < rows.length; row++) {
        // Get columns 
        var currentRow = []
        var cols = rows[row].querySelectorAll("td, th");
        // Iterate through the columns in the current row
        for (var column = 0; column < cols.length; column++) {
            currentRow.push(cols[column].innerText.replace('\r\n', '').replace('\n', ' '));
        }
        // Separate cells with commas
        csv.push(currentRow.join(","));        
    }
    // Download CSV file
    downloadFile(csv.join("\r\n"), filename);
}

/**
 * Export the output of the commands, including stderr, return code, and stdout
 * @param {String} filename 
 */
function exportOutput(filename) {
    var output = [];
    var rows = document.querySelectorAll("table tr");
    for (var i = 1; i < rows.length; i++) {
        var row = [], cols = rows[i].querySelectorAll("td, th");
        row.push('Job Name: ' + cols[0].innerText)
        row.push('Return Code: ' + cols[5].innerText)
        row.push('Standard Out')
        row.push(cols[6].innerText);
        row.push('Standard Error')
        row.push(cols[7].innerText + '\r\n');
        output.push(row.join("\r\n"));               
    }
    downloadFile(output.join("\r\n"), filename);
}