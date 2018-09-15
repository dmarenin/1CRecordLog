from common.orm import models as orm

#region xml_header
def xml_header_start():
    
    return \
        """
        <GanttChart xmlns="http://v8.1c.ru/8.2/data/chart" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="GanttChart">
        """

def xml_header_end_start(date,  now, time_acceptions, time_begin, time_end):
    
    fmt_start = '%Y-%m-%dT'+time_begin+':00'
    fmt_end = '%Y-%m-%dT'+time_end+':59'

    return \
        """
        <drawEmpty>true</drawEmpty>
	<timeScale>
		
      <!--
        <level>
			<measure>Day</measure>
			<interval>1</interval>
			<show>false</show>
			<line width="1" gap="false">
				<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Dotted</style>
			</line>
			<scaleColor>#C0C0C0</scaleColor>
			<dayFormatRule>MonthDayWeekDay</dayFormatRule>
			<format/>
			<labels>
				<ticks>0</ticks>
			</labels>
			<backColor>auto</backColor>
			<textColor>auto</textColor>
			<showPereodicalLabels>true</showPereodicalLabels>

		</level>
        -->
        
        <level>
			<measure>Hour</measure>
			<interval>1</interval>
			<show>true</show>
			<line width="0" gap="true">
				<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Dotted</style>
			</line>
			<scaleColor>#C0C0C0</scaleColor>
			<dayFormatRule>MonthDayWeekDay</dayFormatRule>
			<format>
				<item xmlns="http://v8.1c.ru/8.1/data/core">
					<lang>ru</lang>
					<content>ДФ=Ч</content>
				</item>
				<item xmlns="http://v8.1c.ru/8.1/data/core">
					<lang>#</lang>
					<content>ДФ=Ч</content>
				</item>
			</format>
			<labels>
				<ticks>5</ticks>
			</labels>
			<backColor>auto</backColor>
			<textColor>auto</textColor>
			<showPereodicalLabels>true</showPereodicalLabels>
		</level>

		<level>
			<measure>Minute</measure>
			<interval>""" + str(time_acceptions) + """</interval>
			<show>true</show>
			<line width="0" gap="true">
				<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Dotted</style>
			</line>
			<scaleColor>#C0C0C0</scaleColor>
			<dayFormatRule>MonthDayWeekDay</dayFormatRule>
			<format>
				<item xmlns="http://v8.1c.ru/8.1/data/core">
					<lang>ru</lang>
					<content>ДФ=мм</content>
				</item>
				<item xmlns="http://v8.1c.ru/8.1/data/core">
					<lang>#</lang>
					<content>ДФ=мм</content>
				</item>
			</format>
			<labels>
				<ticks>5</ticks>
			</labels>
			<backColor>#C0D0D0</backColor>
			<textColor>auto</textColor>
			<showPereodicalLabels>true</showPereodicalLabels>
		</level>

		<level>
			<measure>Day</measure>
			<interval>1</interval>
			<show>true</show>
			<line width="1" gap="false">
				<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Solid</style>
			</line>
			<scaleColor>#C0D0D0</scaleColor>
			<dayFormatRule>MonthDayWeekDay</dayFormatRule>
			<format/>
			<labels>
				<label>
					<key>""" + now.strftime('%Y-%m-%dT%H:%M:00') + """</key>
					<text/>
					<lineColor xmlns:d6p1="http://v8.1c.ru/8.1/data/ui/colors/web">d6p1:Red</lineColor>
					<textColor>auto</textColor>
				</label>
				<ticks>0</ticks>
			</labels>
			<backColor>auto</backColor>
			<textColor>auto</textColor>
			<showPereodicalLabels>false</showPereodicalLabels>
		</level>
        
        <transparent>false</transparent>	
		<backColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FieldBackColor</backColor>
		<textColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FormTextColor</textColor>
		<currentLevel>0</currentLevel>
	</timeScale>
	
    <keepScaleVariant>Auto</keepScaleVariant>
	<fixedVariantMeasure>Month</fixedVariantMeasure>
	<fixedVariantInterval>1</fixedVariantInterval>
	<autoFullInterval>false</autoFullInterval>
	<fullIntervalBegin>""" + date.strftime(fmt_start) + """</fullIntervalBegin>
	<fullIntervalEnd>""" + date.strftime(fmt_end) + """</fullIntervalEnd>
	<visualBegin>""" + date.strftime(fmt_start) + """</visualBegin>
	<intervalDrawType>ThreeDimensional</intervalDrawType>
	<noneVariantChars>4</noneVariantChars>
	<noneVariantMeasure>Hour</noneVariantMeasure>
	<verticalStretch>None</verticalStretch>
	<verticalScrollEnable>true</verticalScrollEnable>
	<showValueText>Right</showValueText>
	<extTitle/>
	<outboundColor>#FFFFFF</outboundColor>
	<backIntervals>
		<collection>
			<ticks>0</ticks>
		</collection>
		<ticks>0</ticks>
	</backIntervals>"""

def xml_header_end_end():
   
   return """
    	<linksColor>#000080</linksColor>
	<linksLine width="1" gap="false">
		<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Dashed</style>
	</linksLine>
</GanttChart>
        """

def xml_header_end_link(curBeginKey, curEndKey):

    return """
    <link>
		<curBeginKey>"""+str(curBeginKey)+"""</curBeginKey>
		<curEndKey>"""+str(curEndKey)+"""</curEndKey>
		<beginKey>"""+str(curBeginKey)+"""</beginKey>
		<endKey>"""+str(curEndKey)+"""</endKey>
		<color>auto</color>
		<linkType>EndBegin</linkType>
	</link>"""

#xml_chart
def xml_chart():

    return \
        """
      <chart>
		<seriesCurId>1</seriesCurId>
		<pointsCurId>0</pointsCurId>
		<isSeriesDesign>true</isSeriesDesign>
		<realSeriesCount>0</realSeriesCount>
		<realExSeriesData>
			<id>1</id>
			<color>#991919</color>
			<line width="2" gap="false">
				<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Solid</style>
			</line>
			<marker>Rhomb</marker>
			<text/>
			<strIsChanged>false</strIsChanged>
			<isExpand>false</isExpand>
			<isIndicator>false</isIndicator>
			<colorPriority>false</colorPriority>
		</realExSeriesData>
		<isPointsDesign>true</isPointsDesign>
		<realPointCount>0</realPointCount>
		<curSeries>-1</curSeries>
		<curPoint>0</curPoint>
		<chartType>Column3D</chartType>
		<circleLabelType>None</circleLabelType>
		<labelsDelimiter>, </labelsDelimiter>
		<labelsLocation>Edge</labelsLocation>
		<lbFormat/>
		<lbpFormat/>
		<labelsColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FormTextColor</labelsColor>
		<labelsFont kind="AutoFont"/>
		<transparentLabelsBkg>true</transparentLabelsBkg>
		<labelsBkgColor>auto</labelsBkgColor>
		<labelsBorder width="1">
			<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ControlBorderType">Single</style>
		</labelsBorder>
		<labelsBorderColor>auto</labelsBorderColor>
		<circleExpandMode>None</circleExpandMode>
		<chart3Dcrd>SouthWest</chart3Dcrd>
		<title/>
		<isShowTitle>false</isShowTitle>
		<isShowLegend>false</isShowLegend>
		<ttlBorder width="0">
			<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ControlBorderType">WithoutBorder</style>
		</ttlBorder>
		<ttlBorderColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:BorderColor</ttlBorderColor>
		<lgBorder width="0">
			<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ControlBorderType">WithoutBorder</style>
		</lgBorder>
		<lgBorderColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:BorderColor</lgBorderColor>
		<chBorder width="1">
			<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ControlBorderType">Single</style>
		</chBorder>
		<chBorderColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:BorderColor</chBorderColor>
		<transparent>false</transparent>
		<bkgColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FieldBackColor</bkgColor>
		<isTrnspTtl>false</isTrnspTtl>
		<ttlColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FieldBackColor</ttlColor>
		<isTrnspLeg>false</isTrnspLeg>
		<legColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FieldBackColor</legColor>
		<isTrnspCh>false</isTrnspCh>
		<chColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FieldBackColor</chColor>
		<ttlTxtColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FormTextColor</ttlTxtColor>
		<legTxtColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FormTextColor</legTxtColor>
		<chTxtColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:FormTextColor</chTxtColor>
		<ttlFont xmlns:style="http://v8.1c.ru/8.1/data/ui/style" ref="style:TextFont" kind="StyleItem"/>
		<legFont xmlns:style="http://v8.1c.ru/8.1/data/ui/style" ref="style:TextFont" kind="StyleItem"/>
		<chFont xmlns:style="http://v8.1c.ru/8.1/data/ui/style" ref="style:TextFont" kind="StyleItem"/>
		<isShowScale>true</isShowScale>
		<isShowScaleVL>true</isShowScaleVL>
		<isShowSeriesScale>true</isShowSeriesScale>
		<isShowPointsScale>true</isShowPointsScale>
		<isShowValuesScale>true</isShowValuesScale>
		<vsFormat/>
		<xLabelsOrientation>Auto</xLabelsOrientation>
		<scaleLine width="1" gap="false">
			<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Solid</style>
		</scaleLine>
		<scaleColor>#A9A9A9</scaleColor>
		<isAutoSeriesName>true</isAutoSeriesName>
		<isAutoPointName>true</isAutoPointName>
		<maxMode>NotDefined</maxMode>
		<maxSeries>4</maxSeries>
		<maxSeriesPrc>30</maxSeriesPrc>
		<spaceMode>Half</spaceMode>
		<baseVal>0</baseVal>
		<isOutline>false</isOutline>
		<realPiePoint>0</realPiePoint>
		<realStockSeries>0</realStockSeries>
		<isLight>true</isLight>
		<isGradient>false</isGradient>
		<isTransposition>false</isTransposition>
		<hideBaseVal>false</hideBaseVal>
		<dataTable>false</dataTable>
		<dtVerLines>true</dtVerLines>
		<dtHorLines>true</dtHorLines>
		<dtHAlign>Right</dtHAlign>
		<dtFormat/>
		<dtKeys>true</dtKeys>
		<paletteKind>Palette32</paletteKind>
		<animation>Auto</animation>
		<rebuildTime>0</rebuildTime>
		<isTransposed>false</isTransposed>
		<autoTransposition>false</autoTransposition>
		<legendScrollEnable>true</legendScrollEnable>
		<surfaceColor>#A90000</surfaceColor>
		<radarScaleType>Circle</radarScaleType>
		<gaugeValuesPresentation>Needle</gaugeValuesPresentation>
		<gaugeQualityBands useTextStr="false" useTooltipStr="false"/>
		<beginGaugeAngle>0</beginGaugeAngle>
		<endGaugeAngle>180</endGaugeAngle>
		<gaugeThickness>5</gaugeThickness>
		<gaugeLabelsLocation>InsideScale</gaugeLabelsLocation>
		<gaugeLabelsArcDirection>false</gaugeLabelsArcDirection>
		<gaugeBushThickness>4</gaugeBushThickness>
		<gaugeBushColor>#A9A9A9</gaugeBushColor>
		<autoMaxValue>true</autoMaxValue>
		<userMaxValue>0</userMaxValue>
		<autoMinValue>true</autoMinValue>
		<userMinValue>0</userMinValue>
		<elementsIsInit>true</elementsIsInit>
		<titleIsInit>true</titleIsInit>
		<legendIsInit>true</legendIsInit>
		<chartIsInit>true</chartIsInit>
		<elementsChart>
			<left>0</left>
			<right>0</right>
			<top>0</top>
			<bottom>0</bottom>
		</elementsChart>
		<elementsLegend>
			<left>0.9857029388403491</left>
			<right>0</right>
			<top>0.0407725321888412</top>
			<bottom>0</bottom>
		</elementsLegend>
		<elementsTitle>
			<left>0.8328025477707002</left>
			<right>0</right>
			<top>0</top>
			<bottom>0.9594017094017091</bottom>
		</elementsTitle>
		<borderColor xmlns:d3p1="http://v8.1c.ru/8.1/data/ui/style">d3p1:BorderColor</borderColor>
		<border width="1">
			<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ControlBorderType">Single</style>
		</border>
		<dataSourceDescription/>
		<isDataSourceMode>false</isDataSourceMode>
		<isRandomizedNewValues>true</isRandomizedNewValues>
		<splineStrain>95</splineStrain>
		<translucencePercent>0</translucencePercent>
		<funnelNeckHeightPercent>10</funnelNeckHeightPercent>
		<funnelNeckWidthPercent>10</funnelNeckWidthPercent>
		<funnelGapSumPercent>3</funnelGapSumPercent>
		<multiStageLinkLine width="1" gap="false">
			<style xmlns="http://v8.1c.ru/8.1/data/ui" xsi:type="ChartLineType">Solid</style>
		</multiStageLinkLine>
		<multiStageLinkColor>#000000</multiStageLinkColor>
	</chart>
    """

#xml_points
def xml_points_start_header_start():

    return \
        """
	<points>
		<testMode>false</testMode>
        """

def xml_points_start_header_end():

    return \
        """
		<autoText>true</autoText>
		<useValuesReverseBehavior>false</useValuesReverseBehavior>
	</points>
        """

#xml_points_value
def xml_points_value_empty():
    
    return \
        """
		<value>
			<itemKey>0</itemKey>
			<key>0</key>
			<parentKey>0</parentKey>
			<leftKey>0</leftKey>
			<rightKey>0</rightKey>
			<extKey>0</extKey>
			<title/>
			<cacheKey>0</cacheKey>
			<font kind="AutoFont"/>
			<picture/>
		</value>
        """

def xml_points_value_0(extKey):
    
    return \
        """
		<value>
			<itemKey>0</itemKey>
			<key>0</key>
			<parentKey>0</parentKey>
			<leftKey>1</leftKey>
			<rightKey>0</rightKey>
			<extKey>"""+str(extKey)+"""</extKey>
			<title/>
			<cacheKey>0</cacheKey>
			<font kind="AutoFont"/>
			<picture/>
		</value>
        """

def xml_points_value(itemKey, rightKey, ref, content):

    return \
        """
        <value>
			<itemKey>"""+str(itemKey)+"""</itemKey>
			<key>"""+str(itemKey)+"""</key>
			<parentKey>0</parentKey>
			<leftKey>0</leftKey>
			<rightKey>"""+str(rightKey)+"""</rightKey>
			<extKey>0</extKey>
			<valueKey xmlns:d4p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d4p1:CatalogRef.Сотрудники">"""+ref+"""</valueKey>
			<title>
				<item xmlns="http://v8.1c.ru/8.1/data/core">
					<lang>#</lang>
					<content>"""+content+"""</content>
				</item>
			</title>
			<cacheKey>"""+str(itemKey)+"""</cacheKey>
			<font kind="AutoFont"/>
			<picture/>
		</value>
        """

def xml_points_content_cache_item(mainColor='#000000', secondColor='#000000', backColor='auto', textColor='auto'):

    return \
        """
		<contentCacheItem>
			<mainColor>"""+mainColor+"""</mainColor>
			<secondColor>"""+secondColor+"""</secondColor>
			<backColor>"""+backColor+"""</backColor>
			<textColor>"""+textColor+"""</textColor>
		</contentCacheItem>
        """

#xml_series
def xml_series_empty():

    return \
        """
	<series>
		<testMode>false</testMode>
		<value>
			<itemKey>0</itemKey>
			<key>0</key>
			<parentKey>0</parentKey>
			<leftKey>0</leftKey>
			<rightKey>0</rightKey>
			<extKey>0</extKey>
			<title/>
			<cacheKey>0</cacheKey>
		</value>
		<contentCacheItem>
			<mainColor>#000000</mainColor>
			<secondColor>#000000</secondColor>
			<hatchBetweenIntervalsColor>#000000</hatchBetweenIntervalsColor>
		</contentCacheItem>		
		<autoText>true</autoText>
		<useValuesReverseBehavior>false</useValuesReverseBehavior>
	</series>
        """

def xml_series(date):

    return \
        """
<series>
		<testMode>false</testMode>
		<value>
			<itemKey>0</itemKey>
			<key>0</key>
			<parentKey>0</parentKey>
			<leftKey>1</leftKey>
			<rightKey>0</rightKey>
			<extKey>1</extKey>
			<title/>
			<cacheKey>0</cacheKey>
		</value>
		<value>
			<itemKey>1</itemKey>
			<key>1</key>
			<parentKey>0</parentKey>
			<leftKey>0</leftKey>
			<rightKey>0</rightKey>
			<extKey>0</extKey>
			<valueKey xsi:type="xs:dateTime">"""+date.strftime('%Y-%m-%dT00:00:00')+"""</valueKey>
			<title/>
			<cacheKey>1</cacheKey>
		</value>
		<contentCacheItem>
			<mainColor>#000000</mainColor>
			<secondColor>#000000</secondColor>
			<hatchBetweenIntervalsColor>#000000</hatchBetweenIntervalsColor>
		</contentCacheItem>
		<contentCacheItem>
			<mainColor>#CC0000</mainColor>
			<secondColor>#009966</secondColor>
			<hatchBetweenIntervalsColor>#000000</hatchBetweenIntervalsColor>
		</contentCacheItem>
		<autoText>true</autoText>
		<useValuesReverseBehavior>false</useValuesReverseBehavior>
	</series>
        """

#xml_main_value
def xml_main_interval(intervalKey, data, itemKey, color, content):

    is_receipt = 'false'
    is_repair = 'false'
    is_other = 'false'

    kind_work = ''

    var_a = 'ЗонаПриема'

    if data['kind_work_ref']=='F5C17810-4BE3-4689-88D0-5F7BA50DEBA2':
        is_repair = 'true'
        kind_work = 'Ремонт'
        var_a = 'ЗонаРемонта'
    elif data['kind_work_ref']=='407179CF-91FF-4C9B-A789-A4FDF5E7DB94':
        is_receipt = 'true'
        kind_work = 'Прием'
    else:
        is_other = 'true'
        kind_work = 'Выдача'

    return \
        """
	<interval>
		<itemKey>"""+str(itemKey)+"""</itemKey>
		<key>"""+str(itemKey)+"""</key>
		<begin>"""+data['r_begin'].strftime('%Y-%m-%dT%H:%M:%S')+"""</begin>
		<end>"""+data['r_end'].strftime('%Y-%m-%dT%H:%M:%S')+"""</end>
        <text>
			<item xmlns="http://v8.1c.ru/8.1/data/core">
				<lang>#</lang>
				<content>"""+str(content)+"""</content>
			</item>
		</text>
		
        <details xmlns:d3p1="http://v8.1c.ru/8.1/data/core" xsi:type="d3p1:Structure">
			
            <d3p1:Property name="Сотрудник">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Сотрудники">"""+data['m_ref_ones']+"""</d3p1:Value>
			</d3p1:Property>
			
            <d3p1:Property name="Регистратор">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:DocumentRef.ЗаписьВЖурналЗаписи">"""+data['r_ref_ones']+"""</d3p1:Value>
			</d3p1:Property>
            
            <d3p1:Property name="ПериодНачало">
				<d3p1:Value xsi:type="xs:dateTime">"""+data['r_begin'].strftime('%Y-%m-%dT%H:%M:%S')+"""</d3p1:Value>
			</d3p1:Property>
            <d3p1:Property name="ПериодОкончание">
				<d3p1:Value xsi:type="xs:dateTime">"""+data['r_end'].strftime('%Y-%m-%dT%H:%M:%S')+"""</d3p1:Value>
			</d3p1:Property>
           	
            <d3p1:Property name="ЭтоПрием">
				<d3p1:Value xsi:type="xs:boolean">"""+is_receipt+"""</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ЭтоРемонт">
				<d3p1:Value xsi:type="xs:boolean">"""+is_repair+"""</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ЭтоВыдача">
				<d3p1:Value xsi:type="xs:boolean">"""+is_other+"""</d3p1:Value>
			</d3p1:Property>

            <d3p1:Property name="ВидРаботы">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:EnumRef.ЖурналЗаписиВидРаботы">"""+kind_work+"""</d3p1:Value>
			</d3p1:Property>
            <d3p1:Property name="НомерСтроки">
				<d3p1:Value xsi:type="xs:decimal">"""+str(data['num_str'])+"""</d3p1:Value>
			</d3p1:Property>

            <d3p1:Property name="РежимыРаботыСотрудников">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:EnumRef.РежимыРаботыСотрудниковЖЭЗ">"""+var_a+"""</d3p1:Value>
			</d3p1:Property>

            <!--	          
            
			<d3p1:Property name="СотрудникДолжностьПредставление">
				<d3p1:Value xsi:type="xs:string">Мастер-приемщик</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Период">
				<d3p1:Value xsi:type="xs:dateTime">2018-07-27T00:00:00</d3p1:Value>
			</d3p1:Property>

			<d3p1:Property name="СотрудникРежим">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Сотрудники">f0782c6a-7e95-11e8-9066-d89d6773b964</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="СотрудникДолжность">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Должности">344102ba-4123-11da-900d-0011d882d83d</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Автомобиль">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Автомобили">5260790d-45e5-11e8-8781-d89d6773b964</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Сортировка">
				<d3p1:Value xsi:type="xs:decimal">2</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="АвтоПервыйРазНаТО">
				<d3p1:Value xsi:type="xs:boolean">false</d3p1:Value>
			</d3p1:Property>

			<d3p1:Property name="ОценочнаяТрудоемкость_Диагностика">
				<d3p1:Value xsi:type="xs:decimal">0</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ОценочнаяТрудоемкость_Ремонт">
				<d3p1:Value xsi:type="xs:decimal">5</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="СотрудникПредставление">
				<d3p1:Value xsi:type="xs:string">Перминов Иван</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ЭтоГарантия">
				<d3p1:Value xsi:type="xs:boolean">true</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Организация">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Организации">05a0ce49-bc7d-11de-b5d1-00215e2d3672</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ПричинаОбращения">
				<d3p1:Value xsi:type="xs:string">отзывная по охлжд</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="АвторЗаписи">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Пользователи">fc020001-c8d5-11e6-bfd7-d89d6773b964</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ВидРемонта">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.ВидыРемонта">8b8a54a2-2a6e-11da-9002-0011d882d83d</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ЗаявкаНаРемонт">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:DocumentRef.ЗаявкаНаРемонт">00000000-0000-0000-0000-000000000000</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ЗаказНаряд">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:DocumentRef.ЗаказНаряд">00000000-0000-0000-0000-000000000000</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Подразделение">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.ПодразделенияКомпании">05a0ce4e-bc7d-11de-b5d1-00215e2d3672</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ЗнПроведен">
				<d3p1:Value xsi:type="d3p1:Null"/>
			</d3p1:Property>
			<d3p1:Property name="Телефон">
				<d3p1:Value xsi:type="xs:string">9108906498</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ГосНомер">
				<d3p1:Value xsi:type="xs:string">Т476ХА72</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ПовторныйЗаезд">
				<d3p1:Value xsi:type="xs:boolean">false</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ОтметкаДозвона">
				<d3p1:Value xsi:type="xs:boolean">false</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Комментарий">
				<d3p1:Value xsi:type="xs:string">Запись из карточки клиента</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Контрагент">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Контрагенты">446a52e2-45e6-11e8-8781-d89d6773b964</d3p1:Value>
			</d3p1:Property>
			
			<d3p1:Property name="БизнесПроцессСервис_Организация">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.Организации">05a0ce49-bc7d-11de-b5d1-00215e2d3672</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="БизнесПроцессСервис_Пустая">
				<d3p1:Value xsi:type="xs:boolean">false</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ВремяРемонтаНеизвестно">
				<d3p1:Value xsi:type="xs:boolean">true</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="БизнесПроцессСервис_Гарантия">
				<d3p1:Value xsi:type="xs:boolean">true</d3p1:Value>
			</d3p1:Property>

			<d3p1:Property name="МультибрендПодразделение">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.ПодразделенияКомпании">00000000-0000-0000-0000-000000000000</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ВремяВыдачиНеизвестно">
				<d3p1:Value xsi:type="xs:boolean">true</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="НеПриехал">
				<d3p1:Value xsi:type="xs:boolean">false</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="СкриптРазговора">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:DocumentRef.СкриптРазговора">00000000-0000-0000-0000-000000000000</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="БезПриемаВыдачи">
				<d3p1:Value xsi:type="xs:boolean">false</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Заказчик">
				<d3p1:Value xmlns:d5p1="http://v8.1c.ru/8.1/data/enterprise/current-config" xsi:type="d5p1:CatalogRef.CRM_Клиенты">642dddd2-4b89-11e8-8781-d89d6773b964</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ПериодЖурнал">
				<d3p1:Value xsi:type="xs:dateTime">2018-07-27T09:09:09</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="ДатаСозданияС">
				<d3p1:Value xsi:type="xs:dateTime">2018-07-27T09:09:09</d3p1:Value>
			</d3p1:Property>
			<d3p1:Property name="Регистратор_ПроцессыСервисаКоличествоБольше1">
				<d3p1:Value xsi:type="xs:boolean">false</d3p1:Value>
			</d3p1:Property>
            -->

		</details>
		<color>"""+color+"""</color>
		<intervalKey>"""+str(intervalKey)+"""</intervalKey>
	</interval>
        """

def xml_main_value(itemKey, r_ref):
    
    editFlag = 'false'

    if not r_ref is None:
        editFlag = 'true'

    return \
        """
	<value>
        <itemKey>"""+str(itemKey)+"""</itemKey>
		<key>"""+str(itemKey)+"""</key>
		<text/>
		<editFlag>"""+editFlag+"""</editFlag>
		<backColor>auto</backColor>
		<textColor>auto</textColor>
		<mainColor>auto</mainColor>
		<secondColor>auto</secondColor>
	</value>
        """
