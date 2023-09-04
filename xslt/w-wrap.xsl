<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"  
  xmlns:tei="http://www.tei-c.org/ns/1.0">
  
  <!-- The fix to the empty xmlns attributes was inspired by this post:
  
    https://stackoverflow.com/questions/62465752/how-can-i-avoid-the-xmlns-namespace-attribute-passing-to-child-elements-in-xslt
    
  -->
  
  <!-- XSLT Template to copy anything, priority="-1" -->
  <xsl:template match="@*|node()" priority="-1">
    <xsl:copy>
      <xsl:apply-templates select="@*|node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="tei:text//tei:p//text()">
    <xsl:analyze-string regex="(\w+|;+)" select=".">
      <xsl:matching-substring>
        <xsl:element name="w" namespace="http://www.tei-c.org/ns/1.0">
          <xsl:value-of select="."/>
        </xsl:element>
      </xsl:matching-substring>
      <xsl:non-matching-substring>
        <xsl:value-of select="."/>
      </xsl:non-matching-substring>
    </xsl:analyze-string>
  </xsl:template>
</xsl:stylesheet>
