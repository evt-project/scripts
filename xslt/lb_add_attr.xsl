<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:tei="http://www.tei-c.org/ns/1.0"
version="2.0">
        
    
    <xsl:template match="/">
        <xsl:variable name="filename" select="tokenize(base-uri(.), '/')[last()]"/>
       	<xsl:variable name="filenamepart" select="tokenize($filename, '\.')"/>
       	<xsl:variable name="filenamepart1"><xsl:value-of select="$filenamepart[1]"/></xsl:variable>
       	<xsl:result-document method="xml" href="{$filenamepart1}_2.xml" indent="no">
            <xsl:apply-templates/>
        </xsl:result-document>
    </xsl:template>
    
    <!-- regola per copiare ogni cosa -->
    <xsl:template match="*|@*|text()">
        <xsl:copy>
            <xsl:apply-templates select="*|@*|text()"></xsl:apply-templates>
        </xsl:copy>
    </xsl:template>
    
    
    <xsl:template match="tei:lb">
        <!-- Seleziono @n del pb-->
        <xsl:variable name="pb" select="preceding::tei:pb[1]/@n"/>
        <!-- Aggiungo alla stringa @n una 'Z' in modo da non ottenere una stringa vuota nel passaggio successivo nel caso in cui la stringa fosse fatta di soli numeri -->
        <xsl:variable name="vS" select="concat($pb,'Z')"></xsl:variable>
        <!-- Seleziono la parte numerica del @n -->
        <xsl:variable name="pb_n" select="substring-before(translate($vS,translate($vS,'0123456789',''),'Z'),'Z')"/>
        <!-- seleziono in numero di pagina (aggiungendo anche gli 0 davanti al numero se questo ha meno di 3 cifre) -->
        <xsl:variable name="pb_n_ok" select="if (string-length($pb_n) = 1) then (concat('00',$pb))
                                            else if (string-length($pb_n) = 2) then (concat('0',$pb))
                                            else ($pb)"/>
        
        <!-- seleziono in numero di riga (aggiungendo anche uno 0 davanti al numero se questo ha solo 1 cifra) -->
        <xsl:variable name="n" select="if(string-length(@n) &gt; 1) then(@n)
                                       else(concat('0',@n))"/>
        <xsl:copy>
            <!-- aggiungo attributo @facs -->
            <xsl:attribute name="facs">#VB_line_<xsl:value-of select="$pb_n_ok,$n" separator="_"/></xsl:attribute>
            <!-- aggiungo attributo @facs -->
            <xsl:attribute name="xml:id">VB_lb_<xsl:value-of select="$pb_n_ok,$n" separator="_"/></xsl:attribute>
            <xsl:copy-of select="@*"></xsl:copy-of>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>