<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:tei="http://www.tei-c.org/ns/1.0"
      xmlns="http://www.tei-c.org/ns/1.0"
      exclude-result-prefixes="tei"
      version="1.0">
 <!-- Parameter to pass to the stylesheet, assumes 'w' if nothing given -->
<xsl:param name="e" select="'w'"/>
 <!-- If it exists, a prefix string: include a separator, like 'text1_' to get 'text1_p0005' -->
 <xsl:param name="pre"/>

    <!-- typical copy-all template -->
<xsl:template match="@*|node()|comment()|processing-instruction()" priority="-1">
    <xsl:copy><xsl:apply-templates select="@*|node()|comment()|processing-instruction()"/></xsl:copy>
</xsl:template>

<!-- higher priority one to match elements -->
    <xsl:template match="*" >
        <xsl:copy>
            <!-- If the local-name is the element we've passed it, and there is not an @xml:id attribute  -->
            <xsl:if test="local-name() = $e and not(@xml:id)">
                <!-- make a variable numbering current nodes at any level from tei:text -->
                <xsl:variable name="num"><xsl:number level="any" from="tei:text" format="1111"/></xsl:variable>
                <!-- Then create an @xml:id attribute with the name and the number concatenated -->
                <xsl:attribute name="xml:id"><xsl:value-of select="concat($pre, local-name(), $num)"/></xsl:attribute>
            </xsl:if>
            <!-- apply any other templates (i.e. copy other stuff) -->
            <xsl:apply-templates select="@*|node()|comment()|processing-instruction()"/></xsl:copy>
    </xsl:template>
</xsl:stylesheet>

