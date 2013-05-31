--[[
Based on https://github.com/ArchiveTeam/wget-lua-forum-scripts/blob/master/vbulletin.lua
--]]

read_file = function(file, amount)
  local f = io.open(file)
  local data = f:read(amount)
  f:close()
  return data
end

url_count = 0

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
  if url_count % 100 == 0 then
    print(" - Downloaded "..url_count.." URLs")
  end

  -- Read 32KB in case the feed has a really long title
  local page = read_file(file, 32768) -- returns nil if file is empty
  if not page or string.sub(page, 0, 1) ~= "{" then
    -- page has no JSON (probably a 404 page)
    return {}
  end

  local continuation = string.match(page, '"continuation":"(C..........C)"')
  if continuation then
    return {{url=url_with_continuation(url, continuation), link_expect_html=0}}
  end

  return {}
end
