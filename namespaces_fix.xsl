<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    
    <xsl:variable name="vTeiNamespace" select="'http://www.tei-c.org/ns/1.0'"/>

    <xsl:output indent="yes" method="xml" encoding="utf-8" />
    
    <!-- write tei namespace into TEI element (and strip tei prefix from other elements, cf. other templates) -->
    <xsl:template match="*[local-name()='TEI']">
        <xsl:element name="{local-name()}">
            <xsl:namespace name="tei" select="$vTeiNamespace"/>
            <xsl:attribute name="xml:lang"><xsl:value-of select="'ger'"/></xsl:attribute>
            <xsl:apply-templates select="@* | node()"/>
        </xsl:element>
    </xsl:template>

    <xsl:template match="*">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="@* | node()"/>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="@*">
        <xsl:attribute name="{local-name()}">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    
    <!-- keep closing tag for empty elements -->
    <xsl:template match="*[count(child::*)=0][string-length(text())=0]">
        <xsl:element name="{local-name()}">
            <xsl:apply-templates select="@* | node()"/>
            <xsl:text><!-- force closing tag -->
            </xsl:text>
        </xsl:element>
    </xsl:template>
    
    <!-- keep stuff like "xml:id" -->
    <xsl:template match="@*[string-length(substring-before(name(), ':')) != 0]">
        <xsl:attribute name="{name()}">
            <xsl:value-of select="."/>
        </xsl:attribute>
    </xsl:template>
    
    <xsl:template match="comment() | text() | processing-instruction()">
        <xsl:copy/>
    </xsl:template>

</xsl:stylesheet>
