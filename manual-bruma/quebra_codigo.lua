-- Permite quebrar linha em código no meio do texto (caminhos, URLs, nomes longos)
-- depois de / \ . _ - :  sem alterar o que aparece.
local BS = "\1"   -- marcador temporário para a barra invertida
local function esc(s)
  s = s:gsub("\\", BS)
  s = s:gsub("([#$%%&_{}])", "\\%1")
  s = s:gsub("~", "\\textasciitilde{}")
  s = s:gsub("%^", "\\textasciicircum{}")
  return s
end
function Code(el)
  if FORMAT:match("latex") then
    local t = esc(el.text)
    t = t:gsub("([/%.:%-])", "%1\\allowbreak{}")
    t = t:gsub("(\\_)", "%1\\allowbreak{}")
    t = t:gsub(BS, "\\textbackslash\\allowbreak{}")
    return pandoc.RawInline("latex", "\\texttt{" .. t .. "}")
  end
end
