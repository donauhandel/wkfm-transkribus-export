<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
    xmlns:local="local"
    xmlns="http://www.tei-c.org/ns/1.0"
    exclude-result-prefixes="#all"
    version="3.0">
        <xsl:template match="@* | node()">
        <xsl:copy>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:copy>
    </xsl:template>
    
    
    <xsl:template match="tei:comment[@comment]">
        <xsl:variable name="commentText">
            <xsl:value-of select="replace(@comment, '\\u0020', ' ')"/>
        </xsl:variable>
        <seg type="editorial_comment_seg">
            <xsl:apply-templates/>
            <note type="editorial_comment_note"><xsl:value-of select="$commentText"/></note>
        </seg>
    </xsl:template>
</xsl:stylesheet>