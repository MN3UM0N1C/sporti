import requests

http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=basket_10

with open('example.txt', 'w') as file:
    file.write(requests.get("http://www.goalserve.com/getfeed/401117231212497fb27a08db8de47c17/getodds/soccer?cat=basket_10"))

