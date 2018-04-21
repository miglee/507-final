from couchsurfing import *
import unittest



class Testgetinfo(unittest.TestCase):

    def test_get_number_userlinks(self):
        parser = Parser()
        result =parser.get_resultnumber_userlinks('newyork',1)

#retrieved number
        self.assertTrue(int(result[0])>0)
#retrieved Userlinks
        self.assertTrue(len(result[1])> 0)
        self.assertTrue("http" in result[1][1])

    def test_get_userinfo(self):
        parser = Parser()
        result = parser.get_user_info("https://www.couchsurfing.com/people/the_juanderer")

        self.assertEqual(result[0],"the_juanderer")
        self.assertEqual(int(result[2]),39)
        self.assertEqual(int(result[4]),2009)

class Testinsertdata(unittest.TestCase):

    def test_insert_data_to_db(self):

        insert_pyobject_data_into_db('test',0,[['test','test',0,'test',0]])

        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        statement = "select Name from Users "
        cur.execute(statement)
        usernamelist = []
        for row in cur:
            usernamelist.append(row[0])

        self.assertTrue("test" in usernamelist)

        statement = "select AreaName from Areas "
        cur.execute(statement)
        arealist = []
        for row in cur:
            arealist.append(row[0])

        self.assertTrue("test" in arealist)

        statement = "delete from Users where Name = 'test' "
        cur.execute(statement)
        statement = "delete from Areas where AreaName = 'test'"
        cur.execute(statement)
        conn.commit()
        conn.close()

class Testinteraction(unittest.TestCase):

    def test_process_command(self):

#all possible sets of available command covered to make sure they all work
        try:
            process_command('luckystar unitedstates')
            process_command('luckystar all')
        except:
            self.fail()

        try:
            process_command('number all')
            process_command('number russia,unitedstates')
        except:
            self.fail()

        try:
            process_command('gender all')
            process_command('gender chicago,sanfrancisco')
        except:
            self.fail()
        try:
            process_command('age area all')
            process_command('age area taiwan,unitedstates,france')
            process_command('age gender all')
            process_command('age gender unitedstates')
        except:
            self.fail()
        try:

            process_command('help')
        except:
            self.fail()

        try:
            process_command('invalid input')
        except:
            self.fail()

        try:
            process_command('exit')
        except:
            self.fail()



if __name__ == '__main__':
    unittest.main()