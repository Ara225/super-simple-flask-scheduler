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
/**
 * Confirm all fields contained within the div supplied as elementToCheck are completed
 * @param {Number} groupNumber The number of the group
 * @param {String} elementToCheck The ID of a div that contains the text and textarea field
 */
function confirmAllFieldsCompleted(groupNumber, elementToCheck) {
    for (var i = 0; i<document.getElementById(elementToCheck).childNodes.length; i++) {
        if (document.getElementById('Group'+groupNumber).childNodes[i].type == 'text' || document.getElementById('Group'+groupNumber).childNodes[i].type == 'textarea') {
            if (document.getElementById('Group'+groupNumber).childNodes[i].value == '') {
                alert('All fields are required');
                return false;
            }
        }
    }
    var nextGroup = groupNumber+1;
    document.getElementById('Group' + groupNumber).hidden = true; 
    document.getElementById('Group' + nextGroup).hidden = false;
}

/**
 * Some client side validation 
 * TODO This is BAD think of something better
 * @param {Number} groupNumber The number of the group
 * @param {String} classNameOfDependantElements A class name shared between the dependant elements - One of these most be filled in
 * @param {Array<String>} IDsOfRequiredFields A list of the field ID that must be filled in
 */
function confirmFieldsCompleted(groupNumber, classNameOfDependantElements, IDsOfRequiredFields) {
    // Confirm that the required fields are all completed
    var countCompletedRequiredFields = 0;
    for (var i = 0; i<IDsOfRequiredFields.length; i++) {
        if (document.getElementById(IDsOfRequiredFields[i]).value == '') {
            countCompletedRequiredFields++
        }
    }
    // Confirm that at least one of the Dependent fields is completed
    var countCompletedDependentFields = 0;
    var DependantElements = document.getElementsByClassName(classNameOfDependantElements)
    for (var i2 = 0; i2<DependantElements.length; i2++) {
        if (DependantElements[i2].value != '' && !DependantElements[i2].type.includes('checkbox')) {
            countCompletedDependentFields++
        }
        else if (DependantElements[i2].checked == true) {
            countCompletedDependentFields++
        }
    }
    if (countCompletedRequiredFields != IDsOfRequiredFields.length && countCompletedRequiredFields != 0) {
       alert('Required fields blank');
       return false;
    }
    else if (countCompletedDependentFields != 1) {
        alert('Required fields blank');
        return false;
    }
    countCompletedDependentFields != 1
    var nextGroup = groupNumber+1;
    document.getElementById('Group' + groupNumber).hidden = true; 
    document.getElementById('formSubmit').disabled = false;
    document.getElementById('Group' + nextGroup).hidden = false;
}