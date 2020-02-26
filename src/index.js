/* ***** BEGIN LICENSE BLOCK *****
 *
 * Copyright (C) 2020 Namit Bhalla (oyenamit@gmail.com)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.

 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.

 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>
 *
 * ***** END LICENSE BLOCK ***** */



const AWS = require('aws-sdk');
const doc = new AWS.DynamoDB.DocumentClient();

exports.handler = function(event, context) {

    // ---------------------------------------------------------------------------------------------
    // Avoid poison pill by always returning success/failure
    // ---------------------------------------------------------------------------------------------
    try {
        console.log('Received event:', JSON.stringify(event, null, 2));

        const tableName = process.env.TABLE_NAME;
        let items = [];

        // -----------------------------------------------------------------------------------------
        // Extract and parse each record from Kinesis stream and prepare it to be stored in DB
        // -----------------------------------------------------------------------------------------
        event.Records.forEach(function(record) {
            let data = new Buffer(record.kinesis.data, 'base64').toString('ascii');
            console.log('Received data:', data);

            let tweet = JSON.parse(data);

            if((tweet === undefined) || tweet.user === undefined)
            {
                console.log('Invalid JSON or tweet ' + tweet.user);
                return context.done; 
            }

            console.log('User:', tweet.user.name);
            console.log('Timestamp:', tweet.created_at);

            items.push({
                PutRequest: {
                    Item: {
                        Username: tweet.user.name,
                        Id: tweet.id_str,
                        Timestamp: new Date(tweet.created_at.replace(/( \+)/, ' UTC$1')).toISOString(),
                        Message: tweet.text
                    }
                }
            });
        });


        // -----------------------------------------------------------------------------------------
        // If there are no items to be stored in db, bail out
        // -----------------------------------------------------------------------------------------
        if(items.length < 1)
        {
            console.log('No items to be stored in db');
            return context.done();
        }

        let entries = {};
        entries[tableName] = items;
        writeDB(entries, 0, context);
    }
    catch(e) {
        return context.fail(e);
    }
};


// -------------------------------------------------------------------------------------------------
// Helper function for writing items to DB
// -------------------------------------------------------------------------------------------------
function writeDB(items, retries, context) {
    doc.batchWrite({ RequestItems: items })
        .promise()
        .then((data) => {
            if(Object.keys(data.UnprocessedItems).length) {
                console.log('Unprocessed items remain, retrying.');
                let delay = Math.min(Math.pow(2, retries) * 100, context.getRemainingTimeInMillis() - 200);
                setTimeout(function() {writeDB(data.UnprocessedItems, retries + 1)}, delay);
            } else {
                context.succeed();
            }
        })
        .catch((err) => {
            console.log('DDB call failed: ' + err, err.stack);
            return context.fail(err);
        });   
}

