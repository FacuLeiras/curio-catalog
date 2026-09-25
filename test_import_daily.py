import datetime as dt
import unittest
from import_daily import choose
class Limits(unittest.TestCase):
 def setUp(self):
  self.day=dt.date(2026,9,25)
  self.queue=[{'video_url':str(i),'topic':['philosophy','science','mobility'][i%3]} for i in range(15)]
 def existing(self,ids,timestamp):return [dict(self.queue[i],created_at=timestamp) for i in ids]
 def test_rerun_and_duplicate(self):
  rows=self.existing([0,1],'2026-09-25T12:00:00+00:00')
  chosen=choose(self.queue,rows,today=self.day)
  self.assertEqual(len(chosen),1);self.assertNotIn(chosen[0]['video_url'],{'0','1'})
  rows.append(dict(chosen[0],created_at='2026-09-25T12:01:00+00:00'))
  self.assertEqual(choose(self.queue,rows,today=self.day),[])
 def test_cap(self):self.assertEqual(len(choose(self.queue,self.existing([0,1],'2026-09-24T12:00:00+00:00'),catalog_cap=3,today=self.day)),1)
 def test_local_day(self):self.assertEqual(len(choose(self.queue,self.existing([0,1,2],'2026-09-25T02:00:00+00:00'),today=self.day)),3)
 def test_exhaustion(self):self.assertEqual(choose(self.queue,self.existing(range(15),'2026-09-24T12:00:00+00:00'),today=self.day),[])
if __name__=='__main__':unittest.main()
