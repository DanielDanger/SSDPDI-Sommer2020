const { ZBClient, Duration } = require('zeebe-node')
require("dotenv").config();

const zbc = new ZBClient()

// const res = zbc.publishMessage({
//     correlationKey: 1,
//     messageId: "Message_1ybz4w0",
//     name: 'event-there',
//     variables: { valueToAddToWorkflowVariables: '1', status: 'PROCESSED' },
//     timeToLive: Duration.seconds.of(10), // seconds
// })

async function main() {
    await zbc.publishMessage({
        correlationKey: "1",
        name: "Stress Event",
        variables: { status: "PROCESSED" }
    })
}

main();