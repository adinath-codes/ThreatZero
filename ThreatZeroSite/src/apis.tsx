import axios from "axios";

const API_BASE_URL = "https://api.threatzero.ai";

export const fetchRisks = async ()=>{
    const response = await axios.get(`${API_BASE_URL}/api/dashboard/stats/risks`);
    return response.data;
}

//{"level": "INFO", "message": "\ud83d\udc1d Honeypot command executed: id=1' UN/**/ION/**/SEL/**/ECT table_name FROM information_schema.tables --", "payload": "id=1' UN/**/ION/**/SEL/**/ECT table_name FROM information_schema.tables --",  "system_response": "table_name\n------------\nusers\nproducts\norders\nadmi"
export const fetchLogs = async ()=>{
    const response = await axios.get(`${API_BASE_URL}/api/dashboard/stats/logs`);
    return response.data;
    // "source": "Honeypot", "attacker_ip": "Unknown" , "verdict": "Post-Compromise", "action_taken": "Executed Fake Command"
}

