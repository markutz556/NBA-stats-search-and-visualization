#!/usr/bin/env python
from final_project import *
import unittest

class TestDatabase(unittest.TestCase):
    def test_teams_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = 'SELECT Name FROM Teams'
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Boston Celtics',), result_list)
        self.assertEqual(len(result_list), 30)

        sql = '''
            SELECT Name, ArenaLocation_lat
            FROM Teams
            WHERE Name="Chicago Bulls"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        #print(result_list)
        self.assertEqual(len(result_list), 1)
        self.assertEqual(result_list[0][1], '41.8806908')

        conn.close()

    def test_players_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT No, Name
            FROM Players
            WHERE Name="Kyrie Irving"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn((11,'Kyrie Irving'), result_list)
        self.assertEqual(len(result_list), 1)

        conn.close()

    def test_routes_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Team1
            FROM Routes
        '''
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertTrue(result_list.startswith('@') or result_list.startswith('vs'))

        conn.close()

    def test_points_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT Score5
            FROM Points
        '''
        results = cur.execute(sql)
        result_list = results.fetchone()[0]
        self.assertTrue(result_list.startswith('@') or result_list.startswith('vs'))

        conn.close()

    def test_joins(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql = '''
            SELECT t.Name
            FROM Players as p
                JOIN Teams as t
                ON p.TeamId=t.Id
            WHERE p.Name="James Harden"
        '''
        results = cur.execute(sql)
        result_list = results.fetchall()
        self.assertIn(('Houston Rockets',), result_list)
        conn.close()

class TestSearch(unittest.TestCase):

    def test_get_teams(self):
        self.team = get_all_teams()
        self.assertEqual(len(self.team), 30)
        self.assertIn("Boston Celtics", self.team)

    def test_get_players(self):
        self.player = get_players('Utah Jazz')
        self.assertEqual(len(self.player), 17)
        self.assertIn('Donovan Mitchell',self.player)

    def test_get_route(self):
        self.route = get_team_route('Boston Celtics')
        self.assertEqual(len(self.route), 6)
        self.assertEqual(self.route[0], 'Boston Celtics')
        self.assertTrue(self.route[1].startswith('@') or self.route[1].startswith('vs'))
 
    def test_get_points(self):
        self.point = get_points("Vince Carter")
        self.assertEqual(len(self.point), 6)
        self.assertEqual(self.point[0], 'Vince Carter')
        self.assertTrue(self.point[1].startswith('@') or self.point[1].startswith('vs'))

    def test_get_preteam(self):
        self.preteam = get_preteam('Kyrie Irving')
        self.assertEqual(len(self.preteam), 3)
        self.assertEqual(self.preteam[0], 'Kyrie Irving')
        self.assertIn('CLE',self.preteam)

class TestMapping(unittest.TestCase):

    # we can't test to see if the maps are correct, but we can test that
    # the functions don't return an error!
    def test_plot_team(self):
        try:
            plot_all_teams()
        except:
            self.fail()

    def test_plot_route(self):
        route = ['Boston Celtics',
                'vs  Grizzlies W 113-98',
                '@  Trail Blazers W 97-95',
                '@  Nuggets L 88-82',
                'vs  Nets W 110-97',
                'vs  Bucks W 113-107']
        try:
            plot_game_route(route)
        except:
            self.fail()

    def test_plot_preteam(self):
        team=['Kyrie Irving','CLE','BOS']
        try:
            plot_team_played(team)
        except:
            self.fail()

    def test_plot_point(self):
        point=get_points("Vince Carter")       
        try:
            plot_point(point)
        except:
            self.fail()

if __name__ == '__main__':
    unittest.main()
