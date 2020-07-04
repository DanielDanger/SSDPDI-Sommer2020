import { ZBClient } from "zeebe-node";
import * as path from "path";
require("dotenv").config();

async function main() {
    const zbc = new ZBClient();
    const filename = path.join(__dirname, "..", "bpmn", "pdi_ZebeeProcess.bpmn");
    await zbc.deployWorkflow(filename);
    const res = await zbc.createWorkflowInstance("stress-process", {})
    // const res = await zbc.createWorkflowInstance("stress-process", { eventType: "2", status: "cool" })
    console.log(res);
}

main();