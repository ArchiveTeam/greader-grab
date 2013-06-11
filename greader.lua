--[[
Based on https://github.com/ArchiveTeam/wget-lua-forum-scripts/blob/master/vbulletin.lua
--]]

read_file = function(file, amount)
  local f = io.open(file)
  local data = f:read(amount)
  f:close()
  return data
end

-- Yes, really, lua does not come with an API to popen without a shell, or escape
-- a shell argument.
ensure_safe_and_quote_shell_arg = function(arg)
  -- http://pubs.opengroup.org/onlinepubs/009695399/utilities/xcu_chap02.html
  assert(string.find(arg, "[\\`$\"\'\n\r\t\b\f\v]") == nil, "Argument contains unsafe characters: " .. arg)
  -- Must use single quote
  return "'" .. arg .. "'"
end

read_gz_file = function(file, amount)
  local p = io.popen("gunzip -c -- " .. ensure_safe_and_quote_shell_arg(file))
  local data = p:read(amount)
  p:close()
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

  if not file then
    return {}
  end

  local magic = read_file(file, 2) -- returns nil if file is empty
  if not magic then
    return {}
  end

  -- Support both gzip and uncompressed responses
  -- Read 32KB in case the feed has a really long title
  -- Magic bytes from http://www.gzip.org/zlib/rfc-gzip.html
  -- Note that Lua escapes are decimal, not octal
  local page
  if magic == "\031\139" then
    page = read_gz_file(file, 32768) -- returns nil if file is empty
  else
    page = read_file(file, 32768) -- returns nil if file is empty
  end

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

wget.callbacks.httploop_result = function(url, err, http_stat)
  code = http_stat.statcode
  if not (code == 200 or code == 404) then
    -- Long delay because people like to run with way too much concurrency
    delay = 1200

    io.stdout:write("\nServer returned status "..code.."; this is probably a CAPTCHA page.\n")
    io.stdout:write("You may want to move to another IP.  Waiting for "..delay.." seconds and exiting...\n")
    io.stdout:flush()

    os.execute("sleep "..delay)
    -- We have to give up on this WARC; we don't want to upload anything with
    -- error responses to the upload target
    return wget.actions.ABORT

  else
    return wget.actions.NOTHING
  end
end
