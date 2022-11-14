<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"  
   xpath-default-namespace="http://www.tei-c.org/ns/1.0">
  

  <!-- XSLT Template to copy anything, priority="-1" -->
  <xsl:template match="@*|node()" priority="-1">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="text//p//text()">
    <xsl:analyze-string regex="(\w+|;+)" select=".">
      <xsl:matching-substring>
        <w>
          <xsl:value-of select="."/>
        </w>
      </xsl:matching-substring>
      <xsl:non-matching-substring>
        <xsl:value-of select="."/>
      </xsl:non-matching-substring>
    </xsl:analyze-string>
  </xsl:template>
</xsl:stylesheet>
