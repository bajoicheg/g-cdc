import calendar, datetime, math

def _epoch(text):
 value=datetime.datetime.fromisoformat(text.replace('Z','+00:00'))
 if value.tzinfo is None:raise ValueError('absolute quota reset required')
 return value.timestamp()
def normalize(metadata,account_id,*,now):
 if (metadata.get('status')!='observed' or metadata.get('actual_uid')!=1005
     or metadata.get('identity',{}).get('user_id')!=account_id
     or metadata.get('identity',{}).get('status')!='USER_STATUS_NORMAL'
     or metadata.get('tools_enabled')!=['mcp__cdc__*']
     or metadata.get('extra_usage_policy')!='OWNER_REPORTED_OFF'):
  raise ValueError('actual isolated included-only session required')
 at=_epoch(metadata['observed_at'])
 if not 0<=now-at<=90:raise ValueError('fresh official metadata required')
 expiry=metadata.get('access_expires_at')
 if type(expiry) not in (int,float) or not math.isfinite(expiry) or expiry<now+120:raise ValueError('official token horizon unavailable')
 quota=metadata.get('quota',{})
 if any(not isinstance(quota.get(n),dict) for n in ('limit_5h','limit_month_total','limit_month_code')):raise ValueError('mandatory included windows unavailable')
 windows=[]
 for name in ('limit_5h','limit_7d','limit_month_total','limit_month_code'):
  item=quota.get(name)
  if item is None:continue
  ratio=item.get('used_ratio')
  if type(ratio) not in (int,float) or not math.isfinite(ratio) or not 0<=ratio<=1:raise ValueError('included allowance unavailable')
  end=_epoch(item['reset_time'])
  if name=='limit_5h':duration=18000
  elif name=='limit_7d':duration=604800
  else:
   dt=datetime.datetime.fromtimestamp(end,datetime.timezone.utc);year,month=(dt.year-1,12) if dt.month==1 else (dt.year,dt.month-1)
   previous=dt.replace(year=year,month=month,day=min(dt.day,calendar.monthrange(year,month)[1]));duration=end-previous.timestamp()
  if end<=now:raise ValueError('current reset unavailable')
  windows.append({'name':name,'used_percent':ratio*100,'resets_at':end,'window_seconds':duration})
 return {'provider':'kimi','account_id':account_id,'observed_at':at,'ordinary_usage_allowed':all(w['used_percent']<100 for w in windows),'paid_fallback':False,'required_windows':[w['name'] for w in windows],'windows':windows}
