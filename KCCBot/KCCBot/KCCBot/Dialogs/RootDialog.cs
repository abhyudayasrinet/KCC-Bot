using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using KCCBot.Models;
using Microsoft.Bot.Builder.Dialogs;
using Microsoft.Bot.Connector;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace KCCBot.Dialogs
{
    [Serializable]
    public class RootDialog : IDialog<object>
    {
        public Task StartAsync(IDialogContext context)
        {
            context.Wait(MessageReceivedAsync);

            return Task.CompletedTask;
        }

        private async Task MessageReceivedAsync(IDialogContext context, IAwaitable<object> result)
        {
            var activity = await result as Activity;

            string messageText = activity.Text;
            if (messageText == "hi")
            {
                await context.PostAsync("Hi! Welcome to the KCC Bot. Please type in your query.");
            }
            else
            {
                string query = activity.Text;
                HttpClient client = new HttpClient();
                //client.BaseAddress = new Uri("http://machathon2018.azurewebsites.net/?query=" + query);
                HttpResponseMessage response = await client.GetAsync("http://machathon2018.azurewebsites.net/?query=" + query);
                string responseString = await response.Content.ReadAsStringAsync();

                
                //var details = JObject.Parse(responseString);
                List<Query> answers = JsonConvert.DeserializeObject<List<Query>>(responseString);
                if (answers.Count == 0)
                {
                    string r = "Sorry I couldn't find anything related to this. Let me connect you to the nearest Kisan Call Center.";
                    await context.PostAsync(r);
                }
                else
                {
                    await context.PostAsync("These are the closest matches we have :");
                    foreach (Query answer in answers)
                    {
                        string r = "Title : " + answer.query + "\n\n Answer : " + answer.answer;// + "\n\n Score : " + answer.score.ToString();
                        await context.PostAsync(r);
                    }
                }
                //await context.PostAsync(details["result"]["answer"].ToString());
            }
            context.Wait(MessageReceivedAsync);
        }
    }
}