
Error handling strategy:
All programs check the number of input arguments, wrong numbers of input arguments will exit the program. Moreover, all programs check the json file, and tsv file exist or not on the providing path. On the Task 3 of naive babes classification, "feature_selection.py" only accept the positive integer number of value k.

Instructions:
Please make sure nltk module is installed. Using 'pip3 install nltk'
All programs' execute commands follow the assignment 3 instructions.
Examples for execute commands in my computer are below:
Please drag your file into the terminal, and terminal will show the path of the file. 
All execute commands follows this step.
If examples below is not clear to you, you can follow examples on the assignment instructions. 

For Naive bayes classification and feature selection:
Go to the nbc folder
Task 1: python3 nbc_train.py python3 nbc_train.py /Users/../Desktop/cmput361/ass3/data/train.json /Users/../Desktop/cmput361/ass3/data/bbcmodel.tsv 
Task 2: python3 nbc_inference.py /Users/../Desktop/cmput361/ass3/data/bbcmodel.tsv /Users/../Desktop/cmput361/ass3/data/test.json
Task 3: python3 feature_selection.py /Users/../Desktop/cmput361/ass3/data/train.json 10 /Users/../Desktop/cmput361/ass3/data/train_top_10.json


KNN classification:
Go to the knn folder
Task 5: python3 knn_create_model.py /Users/../Desktop/cmput361/ass3/data/train.json /Users/../Desktop/cmput361/ass3/data/bbcmodel.tsv
Task 6: python3 knn_inference.py /Users/../Desktop/cmput361/ass3/knn/bbc_doc_vectors.tsv 11 /Users/../Desktop/cmput361/ass3/data/test.json

Data structures and Algorithms：
1.In the nbc_inference.py ,feature_selection.py and knn_inference.py we use set to remove repeat terms and use dictionary
to improve the effiency. The detail you can read the comment in the code.
2.In the knn_inference.py, we follow the algorithm in the text book(with Euclidean distance), and use Euclidean norm to imporve the accuracy

Assumptions:
1.In the knn_inference.py, we ignore all terms in the test document that does not have IDF record in the model.
2.feature_selection.py needs 2-3 minutes run for a single k value.
3.knn_inference.py needs 1.5-2 minutes run for a single k value.
4.For a class has both 0 TP and FP, we assumen its F1 value is also 0.

Sources consulted while completing the assignment：
https://www.sciencedirect.com/topics/engineering/euclidean-norm