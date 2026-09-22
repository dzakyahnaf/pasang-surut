$ErrorActionPreference = 'Stop'
$deckFolder = $PSScriptRoot
$deckPath = Join-Path $deckFolder 'Pasang_Surut_Final_ANFORCOM_2026.pptx'
$pdfPath = Join-Path $deckFolder 'Pasang_Surut_Final_ANFORCOM_2026.pdf'
$pptApp = New-Object -ComObject PowerPoint.Application
$presentation = $null
try {
    # WithWindow=false: tidak membuka jendela presentasi pengguna.
    $presentation = $pptApp.Presentations.Open($deckPath, -1, 0, 0)
    $overflow = @()
    foreach ($slide in $presentation.Slides) {
        foreach ($shape in $slide.Shapes) {
            if ($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1) {
                $range = $shape.TextFrame.TextRange
                if ($range.BoundHeight -gt ($shape.Height + 2) -or $range.BoundWidth -gt ($shape.Width + 2)) {
                    $overflow += [PSCustomObject]@{
                        slide = $slide.SlideIndex; shape = $shape.Name; text = $range.Text
                        height = $shape.Height; boundHeight = $range.BoundHeight
                        width = $shape.Width; boundWidth = $range.BoundWidth
                    }
                }
            }
        }
    }
    # Sertakan lampiran yang tersembunyi dalam slideshow biasa pada PDF.
    foreach ($slide in $presentation.Slides) { $slide.SlideShowTransition.Hidden = 0 }
    $presentation.SaveAs($pdfPath, 32)
    $report = [PSCustomObject]@{slides=$presentation.Slides.Count; overflow=@($overflow); pdf=[System.IO.Path]::GetFileName($pdfPath)}
    $report | ConvertTo-Json -Depth 5 | Set-Content (Join-Path $deckFolder 'verifikasi_powerpoint.json') -Encoding UTF8
    $report | ConvertTo-Json -Depth 5
} finally {
    if ($null -ne $presentation) { $presentation.Close() }
    if ($pptApp.Presentations.Count -eq 0) { $pptApp.Quit() }
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($pptApp)
}
