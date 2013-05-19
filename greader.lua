--[[
Based on https://github.com/ArchiveTeam/wget-lua-forum-scripts/blob/master/vbulletin.lua
--]]


read_file = function(file)
  local f = io.open(file)
  local data = f:read("*all")
  f:close()
  return data
end

url_count = 0

json = require("dkjson")

url_with_continuation = function(url, continuation)
  assert(string.len(continuation) == 12, "continuation should be 12 bytes, was " .. string.len(continuation))
  if string.find(url, "%?c=............&") then
    return string.gsub(url, "%?c=............&", "?c=" .. continuation .. "&", 1)
  end
  return string.gsub(url, "%?", "?c=" .. continuation .. "&", 1)
end

wget.callbacks.get_urls = function(file, url, is_css, iri)
  -- progress message
  url_count = url_count + 1
  if url_count % 25 == 0 then
    print(" - Downloaded "..url_count.." URLs")
  end

  local continuation = json.decode(read_file(file))["continuation"]
  if continuation then
    return {{url=url_with_continuation(url, continuation), link_expect_html=0}}
  end
  
  return {}
end
