from tools import inspect_database, execute_query,Long_duration
import uuid
from utils_ import preprocess
from Prompt.analyst_prompt import prompt as analyst_prompt
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, DEFAULT_MODEL
from pandas_ta import rsi,sma, ema,stochrsi, supertrend
import pdb
from Prompt.Prompt_SQL_ANALYSER import prompt as data_engineer_prompt
from config import model_dracarys_llama_instruct,API_KEY,BASE_URL, API_KEY2
from openai import OpenAI
from utils_ import preprocess
from sql_engineer_agent import agent_react_loop as sql_agent_tool
import json
from talib import RSI, SMA, ATR

from tools import *
client = OpenAI(api_key=API_KEY2, base_url=NVIDIA_BASE_URL)
tools = {"sql_agent_tool":sql_agent_tool,"rsi":rsi,"sma":sma,"ema":ema,"stochrsi":stochrsi,"supertrend":supertrend,
         "get_current_datetime":get_current_datetime,
         "get_today_date":get_today_date,
         "Long_duration":long_duration,
         "add_indicator":add_indicator,
         }



def agent(message):
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=message,
        temperature=0.1,
        max_tokens=2000

    )
    return response.choices[0].message.content

def tool_executor(response):
    if "action" in response:
        tool = tools[response.get("action")['tool_name']]
        parameter = response.get("action")['parameters']
        response = tool(**parameter)

    return response


def agent_loop(user_input:str):
    message = [{"role":"system","content":analyst_prompt},
               {"role":"user","content":user_input},
               ]
    return_response = None
    state_ = {}
    while True:
        response = preprocess(agent(message))
        print(response)
        if "finalanswere" in response and type(response["finalanswere"])==dict and response["finalanswere"]['status']!='' and len(response["finalanswere"]['status'])!=0:
            return_response = response
         
            print("Breaking")
            break
        elif "action" in response:
            
            tool_response = tool_executor(response=response)
            if type(tool_response) == pd.DataFrame:
                pdb.set_trace()
                state_[tool_response['Symbol'].unique()[0]] = tool_response
                text = f"Price data fetched fetched successfully. Here is the reference key {tool_response['Symbol'].unique()[0]}, if you want to use the data again you can pass reference key. It contain the following columns {list(tool_response.columns)}"
                message.append({"role":"assistant","content":f"{text}"})
                #return tool_response
            else:
                message.append({"role":"assistant","content":f"{tool_response}"})
        

if __name__ == "__main__":
    user_input = "Get me Activity in the share of garden reach shipbuilders and engineers from 1st May to 13th June 2026 on Daily Time frame" #input("User Input: ")
    analyst_respones = agent_loop(user_input=user_input)
    print(analyst_respones)
