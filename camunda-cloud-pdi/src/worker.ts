import { ZBClient } from "zeebe-node";
import got from "got";

//config for ZeeBe connection
require("dotenv").config();

//ZeeBe Client
const zbc = new ZBClient();

//REST client functions & validation for response
const validJSON = {
    user: "pdissd@quickstart-1592463381049.iam.gserviceaccount.com",
    private_key_id: "6853c54195cc2d04b890f786bb7b3373ac5d8568"
};

async function callGetRequestRestClient(destination: string) {

    let result = await got.get("https://us-central1-beaming-figure-281415.cloudfunctions.net" + destination, {

        headers: {
            'user': validJSON.user,
            'private_key_id': validJSON.private_key_id
        }
    });

    console.log(`Get-call with destination <${destination}> finished with status code: ${result.statusCode}`);
    // console.log(result.body);
    return result.body;
}


async function callPostRequestRestClient(destination: string, payload: any) {


    let result = await got.post("https://us-central1-beaming-figure-281415.cloudfunctions.net" + destination, {

        headers: {
            'user': validJSON.user,
            'private_key_id': validJSON.private_key_id
        },
        json: payload
    });

    console.log(`Post-call with destination <${destination}> finished with status code: ${result.statusCode}`);
    // console.log(result.body);
    return result.body
}



//worker for analyze step
const analyzeWorker = zbc.createWorker("step-calendarAnalyze", async (job, complete, w) => {

    const analyzeResult = await callGetRequestRestClient("/get_events");
    //console.log(job.variables);
    complete.success({ analyseResult: analyzeResult, notifyUser: false });
});

//worker for replanning step
const replanningWorker = zbc.createWorker("step-calendarReplanning", async (job, complete, w) => {

    const replanningResult = await callGetRequestRestClient("/optimize");
    //console.log(job.variables);
    complete.success({ replanningResult });
});

//worker for update step
const updateWorker = zbc.createWorker("step-calendarUpdate", async (job, complete, w) => {


    const { replanningResult } = job.variables;

    let postPayload = JSON.parse(replanningResult);

    const updateResult = await callPostRequestRestClient("/replan_events", postPayload);

    complete.success({ updateResult });
});


