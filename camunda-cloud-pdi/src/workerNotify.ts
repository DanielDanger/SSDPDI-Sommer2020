import { ZBClient } from "zeebe-node";
import got from "got";
import moment from "moment";

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


async function callPostRequestRestClient(destination: string, payload: any, additionalHeaders: any) {


    let result = await got.post("https://us-central1-beaming-figure-281415.cloudfunctions.net" + destination, {

        headers: additionalHeaders,
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
    complete.success({ analyseResult: analyzeResult, notifyUser: true });
});

//worker for replanning step
const replanningWorker = zbc.createWorker("step-calendarReplanning", async (job, complete, w) => {

    const replanningResult = await callGetRequestRestClient("/optimize");
    //console.log(job.variables);
    complete.success({ replanningResult });
});


//worker for notify step
const notifyWorker = zbc.createWorker("step-notifyUser", async (job, complete, w) => {

    let notifyHeader = {
        user: validJSON.user,
        private_key_id: validJSON.private_key_id,
        create: "true"
    }

    var startdate = moment().add(3, 'minute').format("YYYY-MM-DDTHH:mm:ss") + "+02:00";
    var enddate = moment().add(1, 'hour').format("YYYY-MM-DDTHH:mm:ss") + "+02:00";


    let postPayload = {
        "end": {
            "dateTime": enddate
        },
        "start": {
            "dateTime": startdate
        },
        "summary": "ERROR Terminoptimierung nicht möglich",
        "description": "Aufgrund von Überplanung oder Kompexität ist keine Planung möglich. Bitte nutzen Sie folgende Möglichkeiten:\r\n1. Löschen Sie nicht wichtige Termine\r\n2. Ändern Sie ihre Prioritäten",
        "reminders": {
            "overrides": [
                {
                    "method": "email",
                    "minutes": 1
                }
            ],
            "useDefault": false
        }
    };

    const notifyResult = await callPostRequestRestClient("/replan_events", postPayload, notifyHeader);

    complete.success({ notifyResult });
});

//worker for update step
const updateWorker = zbc.createWorker("step-calendarUpdate", async (job, complete, w) => {


    const { replanningResult } = job.variables;

    let postPayload = JSON.parse(replanningResult);

    const updateResult = await callPostRequestRestClient("/replan_events", postPayload, validJSON);

    complete.success({ updateResult });
});


