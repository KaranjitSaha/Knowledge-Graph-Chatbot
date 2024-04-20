from neo4j import GraphDatabase

host = 'bolt://0.0.0.0:7687'
user = 'neo4j'
password = 'pleaseletmein'
driver = GraphDatabase.driver(host, auth=(user, password))


def read_query(query, params={}):
    #print("QUERY : \n " + query)
    with driver.session() as session:
        result = session.run(query, params)
        response = [r.values()[0] for r in result]
        return response


def get_article_text(title):
    # title = [t + ' ' for t in title]
    title = title+" "
    print("TITLE: ",title,"!\n Type of TITLE: "+str(type(title)),"\n")
    # title="Former Australian chief scientist to head review of carbon credit scheme after whistleblower revelations "
    text = read_query(
        "MATCH (a:Article {webTitle:$title}) RETURN a.bodyContent as response",{'title': title})
    # text=read_query("MATCH (a:Article {id:$title}) RETURN a.bodyContent as response",{'title': title})
    return text
