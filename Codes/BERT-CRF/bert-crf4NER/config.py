class Config(object):	
	apr_dir = '/data/pldu/bert_crf/model/'
	data_dir = '/data/pldu/bert_crf/corpus/'
	model_name = 'model_4.pt'
	epoch = 10
	bert_model = 'bert-base-cased' #'SpanBERT/spanbert-base-cased'
	lr = 5e-5
	eps = 1e-8
	batch_size = 32
	mode = 'prediction' # for prediction mode = "prediction"
	training_data = 'eng_train_building.txt'
	val_data = 'eng_test_building.txt'
	test_data = 'eng_test_building.txt'
	test_out = 'test_prediction_v1_last.csv'
	raw_prediction_output = 'raw_prediction.csv'
	raw_text = '../corpus/eng_inference_building_raw.txt'
	loss_type = 'ce'
