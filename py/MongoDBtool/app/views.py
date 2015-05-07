__author__ = 'poojapawara'

from mongoTool import app
from app import conn, db
from flask import render_template, redirect, url_for
from sets import Set
from bson.objectid import ObjectId


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home_page.html')


@app.route('/help')
def help_page():
    return render_template('help_page.html')


@app.route('/databases')
def display_databases():
    db_list = []
    for i in conn.database_names():
        db_list.append(i)

    if db_list.__contains__("local"):
        db_list.remove("local")
    if db_list.__contains__("admin"):
        db_list.remove("admin")
    return render_template('databases.html', databases=db_list)


@app.route('/database/<name>')
def select_database(name):
    global db
    db = getattr(conn, name)

    return redirect(url_for('display_collections'))


@app.route('/database/add/<name>')
def add_database(name):
    global db
    db = getattr(conn, name)

    return redirect(url_for('display_collections'))


@app.route('/database/drop/<name>')
def drop_database(name):
    conn.drop_database(name)
    global db
    db = getattr(conn, 'test')
    return redirect(url_for('display_databases'))


@app.route('/collections')
def display_collections():
    collection_list = []
    for i in db.collection_names():
        collection_list.append(i)

    if collection_list.__contains__("system.indexes"):
        collection_list.remove("system.indexes")
    return render_template('collections.html', collections=collection_list)


@app.route('/signin')
def signin():
    return render_template('signin.html')


@app.route('/tutorial')
def tutorial():
    return render_template('tutorial.html')


@app.route('/collections/<name>')
def show_collection(name):
    db_select = db
    my_collection = getattr(db_select, name)
    content = my_collection.find()

    key_list = Set()

    for i in content:
        for key, value in i.iteritems():
            key_list.add(key)

    content = my_collection.find()

    content_dict_list = []
    for each_row in content:
        content_dict = {}

        orig_content = "{\n"
        orig_content += "\"_id\" : ObjectId(\"" + str(each_row["_id"]) + "\"),"
        for key, value in each_row.iteritems():
            if str(key) == "_id":
                pass
            else:
                list1 = ""
                if type(value) == type(list()):
                    list1 = "["
                    for i in value:
                        list1 += "\"" + str(i) + "\","
                    list1 = list1.rstrip(",")
                    list1 += "]"
                    value_obj = list1
                else:
                    value_obj = value
                orig_content += "\n\"" + str(key) + "\"" + " : " + "\"" + str(value_obj) + "\","
        orig_content = orig_content.rstrip(",")
        orig_content += "\n}"

        list1 = ""
        for key in key_list:
            value = each_row.get(key)
            if type(value) == type(list()):
                for i in value:
                    list1 += str(i) + ","
                list1 = list1.rstrip(",")
                value_obj = list1
            else:
                value_obj = value
            if value_obj is None:
                content_dict[key] = ""
            else:
                content_dict[key] = value_obj

        content_dict_list.append([content_dict, orig_content])

    return render_template('collection_content.html', name=name, keys=key_list,
                           list_new=content_dict_list)


@app.route('/collections/add/<name>/')
def add_collection(name):
    print name
    db_select = db
    my_collection = getattr(db_select, name)
    content = my_collection.insert({})
    content = my_collection.remove({})

    return redirect(url_for('display_collections'))


@app.route('/collections/rename/<old_name>/<new_name>')
def rename_collection(old_name, new_name):
    db_select = db
    my_collection = getattr(db_select, old_name)
    content = my_collection.rename(new_name)

    return redirect(url_for('display_collections'))


@app.route('/collections/delete/<name>')
def delete_collection(name):
    db_select = db
    my_collection = getattr(db_select, name)
    content = my_collection.drop()

    return redirect(url_for('display_collections'))


@app.route('/collections/delete_doc/<name>/<doc_id>')
def delete_doc(name, doc_id):
    db_select = db
    my_collection = getattr(db_select, name)
    doc = ObjectId(str(doc_id))
    content = my_collection.remove({"_id": doc})

    return redirect(url_for('show_collection', name=name))


@app.route('/collections/edit_doc/<name>/<doc_id>/<attr_name>/<attr_value>')
def edit_doc(name, doc_id, attr_name, attr_value):
    db_select = db
    my_collection = getattr(db_select, name)
    doc = ObjectId(str(doc_id))
    content = my_collection.update({"_id": doc}, {"$set": {attr_name: attr_value}})

    return redirect(url_for('show_collection', name=name))


@app.route('/collections/delete_attr/<name>/<doc_id>/<attr_name>')
def delete_attribute(name, doc_id, attr_name):
    db_select = db
    my_collection = getattr(db_select, name)
    doc = ObjectId(str(doc_id))
    content = my_collection.update({"_id": doc}, {"$unset": {attr_name: ""}})

    return redirect(url_for('show_collection', name=name))


@app.route('/collections/<name>/document/<var>/<objectid>')
def route_doc_page(name, var, objectid):
    if var == 'True':
        db_select = db
        my_collection = getattr(db_select, name)
        doc = ObjectId(str(objectid))
        content = my_collection.find({"_id": doc})
        return render_template('doc_add.html', name=name, content=content, objectid=objectid)

    else:
        db_select = db
        my_collection = getattr(db_select, name)
        result = my_collection.insert({})
        doc = ObjectId(str(result))
        content = my_collection.find({"_id": doc})
        return render_template('doc_add.html', name=name, content=content, objectid=result)


@app.route('/collections/<name>/add_document/<objectid>/<attr>/<value>/<option>')
def add_doc(name, objectid, attr, value, option):
    db_select = db
    my_collection = getattr(db_select, name)
    doc = ObjectId(str(objectid))

    if option == "single_value":
        result = my_collection.update({"_id": doc}, {"$set": {attr: value}})
    else:
        my_list = value.split(",")
        result = my_collection.update({"_id": doc}, {"$set": {attr: my_list}})
    return redirect(url_for('route_doc_page', name=name, var='True', objectid=objectid))


@app.route('/collections/add_attr_to_collection/<name>/<attr_name>')
def add_attr_to_collection(name, attr_name):
    db_select = db
    my_collection = getattr(db_select, name)
    content = my_collection.update({}, {"$set": {attr_name: ""}}, upsert=False, multi=True)

    return redirect(url_for('show_collection', name=name))


@app.route('/collections/delete_attr_from_collection/<name>/<attr_name>')
def delete_attr_from_collection(name, attr_name):
    db_select = db
    my_collection = getattr(db_select, name)
    content = my_collection.update({}, {"$unset": {attr_name: ""}}, upsert=False, multi=True)

    return redirect(url_for('show_collection', name=name))


@app.route('/sql_to_mongodb')
def sql_to_mongodb():
    return render_template('sql_to_mongodb_conversion.html')


@app.route('/tutorial/overview')
def mongodb_overview():
    return render_template('mongodb_overview.html')


@app.route('/tutorial/insert_doc')
def insert_doc_tutorial():
    return render_template('insert_doc_tutorial.html')


@app.route('/tutorial/update_doc')
def update_doc_tutorial():
    return render_template('update_doc_tutorial.html')


@app.route('/tutorial/delete_doc')
def delete_doc_tutorial():
    return render_template('delete_doc_tutorial.html')


@app.route('/tutorial/search_doc')
def search_doc_tutorial():
    return render_template('search_doc_tutorial.html')
