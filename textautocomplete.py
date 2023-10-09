from flask import Flask, jsonify, request, redirect, render_template
import GRU  
import time
import random

from tensorflow import keras
from keras.models import load_model
import numpy as np
import pickle

# Load the model and tokenizer
model = load_model('next_words4.h5')
tokenizer = pickle.load(open('token.pkl', 'rb'))

def Predict_Next_Words(model, tokenizer, text):

  sequence = tokenizer.texts_to_sequences([text])
  sequence = np.array(sequence)
  preds = np.argmax(model.predict(sequence))
  predicted_word = ""
  
  for key, value in tokenizer.word_index.items():
      if value == preds:
          predicted_word = key
          break
  
  print(predicted_word)
  return predicted_word

lexicon = {}
app = Flask(__name__)
app.secret_key = "secret key"


import os, json
 
	
@app.route('/')
def upload_form():
	 
	return render_template('index.html')

@app.route('/search', methods=['POST',"GET"])
def search():
	term = request.form['q']
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__)) 
	json_url = os.path.join(SITE_ROOT, "data", "subject_lines.json")
	json_data = json.loads(open(json_url).read()) 
 
	if(term.endswith(" ")):
		term_last_index = len(term.split())-1
		filtered_dict = [v.split()[term_last_index+1] for v in json_data if v.lower().startswith(term.lower()) and len(v.split())>len(term.split()) ]
	else:
		term_last_index = len(term.split())-1
		filtered_dict = [v.split()[term_last_index] for v in json_data if ( term.lower() in (v.lower()) and v.lower().startswith(term.lower()))  ]

	filtered_dict = list(set(filtered_dict))


	print(filtered_dict)
	
	resp = jsonify(filtered_dict)
	resp.status_code = 200
	return resp

@app.route('/autocomplete_text', methods=['POST',"GET"])
def autocomplete_text():
	term = request.form['q']
	text = ""
	text = text + str(term.split()[-3]) + " " + str(term.split()[-2]) + " " + str(term.split()[-1])
	filtered_dict = Predict_Next_Words(model, tokenizer, str(text))
	filtered_dict = [filtered_dict]
	resp = filtered_dict
	print(filtered_dict)
	
	resp = jsonify(filtered_dict)
	resp.status_code = 200
	return resp

subject_lines_file = open("data/sub.txt", encoding="utf8")
subject_lines_content = subject_lines_file.read()
subject_lines = subject_lines_content.split("\n")

template_file = open("data/template.txt", encoding="utf8")
template_file_content = template_file.read()
templates = template_file_content.split("\n\n\n")

temp_gen = {subject_lines[i]: templates[i] for i in range(len(subject_lines))}

def superPos(input_Str):
	for sub in subject_lines:
		if input_Str.lower() in sub.lower():
			return sub
	return -1

@app.route('/result', methods=['POST',"GET"])
def result():
	result_term = request.form['input_text'].strip(" ")
	print ('Result: ', result_term)
	
	if result_term in temp_gen.keys():
		output_result = temp_gen[result_term]
	elif ("Request for " + result_term.strip(" ")) in temp_gen.keys():
		output_result = temp_gen["Request for " + result_term.strip(" ")]
	elif superPos(result_term) != -1:
		output_result = temp_gen[superPos(result_term)]
	else:
		output_result = result_term + ":\n\n" + "Hi, Hope you are doing well. [Your Context]\n\n\nSincerly,\n[Your Name]"
	# output_result = GRU.GRU(result_term)
	print(output_result)

	result_resp = jsonify(output_result)

	# print(result_resp)	 
	result_resp.status_code = 200
	time.sleep(random.randint(5, 7))
	return result_resp

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080) 


