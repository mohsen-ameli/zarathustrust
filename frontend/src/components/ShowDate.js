let formatAMPM = (hours, minutes) => {
    var ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'
    minutes = minutes < 10 ? '0'+minutes : minutes;
    var strTime = hours + ':' + minutes + ' ' + ampm;
    return strTime;
}

const ShowDate = ({year, month, day, hour, minute, seconds, format}) => {
    let date;
    let today;

    day = day - 1
    
    if ((hour && minute && seconds) !== undefined) {
        date = new Date(Date.UTC(year, month-1, day, hour, minute, seconds))

        if (format==="first") {
            today = date.toLocaleString('en-ca', { month: 'long' }) + " " + day + ", " + year
        } else if (format === "second") {
            today = date.toLocaleString('en-ca', { weekday: 'long' }) + " at " + formatAMPM(date.getHours(), date.getMinutes())
        }
    }


    
    return (
        <span className="show-date">
            {today}
        </span>
    );
}
 
export default ShowDate;