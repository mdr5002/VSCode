import ExcelScript from "office-scripts";

function main(workbook: ExcelScript.Workbook) {
    let sheet2 = workbook.getWorksheet("Sheet2");
    let sheet3 = workbook.getWorksheet("Sheet3");

    // Get the range of column A.
    let range = sheet3.getRange("A:A");

    // Find the cell with the word "last".
    let cell = range.find("last", {
        completeMatch: false, // Partial match is allowed.
        matchCase: false, // Case-insensitive search.
    });

    // Check if the cell is found.
    if (cell) {
        // Get the cell one column to the right.
        let adjacentCell = cell.getOffsetRange(0, 1);
        // Get the last used row number in column H.
        let lastRow = sheet3.getRange("H:H").getLastCell().getRowIndex();

        // Get the range from the adjacent cell to column H and down to the last used row.
        let sourceRange = sheet3.getRangeByIndexes(
            adjacentCell.getRowIndex(),
            adjacentCell.getColumnIndex(),
            lastRow - adjacentCell.getRowIndex() + 1,
            7
        );

        // Get the values from the source range.
        let sourceValues = sourceRange.getValues();

        // Get the destination range where the values will be set.
        let destinationRange = sheet3.getRangeByIndexes(
            adjacentCell.getRowIndex(),
            adjacentCell.getColumnIndex(),
            lastRow - adjacentCell.getRowIndex() + 1,
            7
        );

        // Set the values to the destination range.
        destinationRange.setValues(sourceValues);
    } else {
        // Handle the case when the cell is not found.
        console.log("No cell with the word 'last' was found.");
    }
    // Clears the content, formats, and formulas in the range
    let clearCell = sheet2.getRange("B4:H20");
    clearCell.delete;

    let newCell = sheet2.getRange("B4");
    newCell.setValue("-");

    // Set formulas for cells B6, B7, and B8
    let cellB6 = sheet2.getRange("B6");

    cellB6.setFormula(
        `=IF($A10 = "Notes: ", XLOOKUP($B$4, CustTB[Customer account], CustTB[Name], ""), IF($A9 = "Notes: ", XLOOKUP($B$4, CustTB[Customer account], CustTB[Price group], ""), IF($A8 = "Notes: ", XLOOKUP($B$4, CustTB[Customer account], CustTB[Material Agree], ""), ""))`);

    sheet2
        .getRange("B6")
        .autoFill("B6:B50", ExcelScript.AutoFillType.fillDefault);

    const commentCell = sheet2.getRange("B4");

    // Replace with your actual email and name.
    const email = "mrice@kalaswire.com";
    const name = "Michael Rice";

    // Create the mention object.
    const mention = {
        email: email,
        id: 0, // This ID maps this mention to the `id=0` text in the comment.
        name: name,
    };

    // The content of the comment.
    const commentContent = `<at id="0">${name}</at> Please Update`;

    // Add a rich comment with the mention to the active cell.
    workbook.addComment(
        commentCell,
        {
            mentions: [mention],
            richContent: commentContent,
        },
        ExcelScript.ContentType.mention
    );
}
