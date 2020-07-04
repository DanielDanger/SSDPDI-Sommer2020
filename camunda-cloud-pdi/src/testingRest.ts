import * as rm from 'typed-rest-client'
import * as httpm from 'typed-rest-client/HttpClient';
import * as httpI from 'typed-rest-client/Interfaces';
import got from "got";
import * as gotImp from "got";
import moment from "moment";


const validJSON = {
    user: "pdissd@quickstart-1592463381049.iam.gserviceaccount.com",
    private_key_id: "6853c54195cc2d04b890f786bb7b3373ac5d8568"
};

async function callRestClient(destination: string) {



    // let testJSON = JSON.parse(
    //     '[{"kind": "calendar#event", "etag": "\"3186708785634000\"", "id": "6mifnab99iin5rrb48lqff4fad", "status": "confirmed", "htmlLink": "https://www.google.com/calendar/event?eid=Nm1pZm5hYjk5aWluNXJyYjQ4bHFmZjRmYWQgYXFwMHB2MnVpdmdlcWxrOTV2cDYwZmJsM2tAZw", "created": "2020-06-28T14:26:32.000Z", "updated": "2020-06-28T14:26:32.817Z", "summary": "Ergebnis 2", "description": "40,sport", "creator": {"email": "daniel.degenhardt1994@gmail.com"}, "organizer": {"email": "aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com", "displayName": "SSD", "self": true}, "start": {"dateTime": "2020-07-02T21:00:00+02:00"}, "end": {"dateTime": "2020-07-02T22:00:00+02:00"}, "iCalUID": "6mifnab99iin5rrb48lqff4fad@google.com", "sequence": 0, "reminders": {"useDefault": true}}, {"kind": "calendar#event", "etag": "\"3186708826162000\"", "id": "66lnavifoc5b4cnqclsar3op5g", "status": "confirmed", "htmlLink": "https://www.google.com/calendar/event?eid=NjZsbmF2aWZvYzViNGNucWNsc2FyM29wNWcgYXFwMHB2MnVpdmdlcWxrOTV2cDYwZmJsM2tAZw", "created": "2020-06-28T14:26:53.000Z", "updated": "2020-06-28T14:26:53.081Z", "summary": "Ergebnis 3", "description": "20,work", "creator": {"email": "daniel.degenhardt1994@gmail.com"}, "organizer": {"email": "aqp0pv2uivgeqlk95vp60fbl3k@group.calendar.google.com", "displayName": "SSD", "self": true}, "start": {"dateTime": "2020-07-03T20:30:00+02:00"}, "end": {"dateTime": "2020-07-03T21:30:00+02:00"}, "iCalUID": "66lnavifoc5b4cnqclsar3op5g@google.com", "sequence": 0, "reminders": {"useDefault": true}}]')

    // testJSON

    let response = await got.get("https://us-central1-beaming-figure-281415.cloudfunctions.net" + destination, {

        headers: {
            'user': validJSON.user,
            'private_key_id': validJSON.private_key_id
        }

    });

    // let response = await got.post("https://us-central1-beaming-figure-281415.cloudfunctions.net" + destination, {
    //     json: validJSON
    // });

    console.log(response.body);

}

//callRestClient("/optimize");

//runSample();"/get_events"

function testfunktion() {

    var startdate = moment().add(1, 'minute').format("YYYY-MM-DDTHH:mm:ss");
    var enddate = moment().add(1, 'hour').format("YYYY-MM-DDTHH:mm:ss");

    console.log(startdate);
    console.log(enddate);

}

testfunktion();