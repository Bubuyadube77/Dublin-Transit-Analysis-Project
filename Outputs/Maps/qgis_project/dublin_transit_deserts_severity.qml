<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.34" styleCategories="Symbology">
  <renderer-v2 type="graduatedSymbol" attr="desert_severity_index" forceraster="0" enableorderby="0" graduatedMethod="GraduatedColor">
    <ranges>
      <range lower="-1.000000" upper="-0.500000" label="-1.0 to -0.5 (well-served, low-need)" render="true" symbol="0"/>
      <range lower="-0.500000" upper="0.000000" label="-0.5 to 0.0" render="true" symbol="1"/>
      <range lower="0.000000" upper="0.500000" label="0.0 to 0.5" render="true" symbol="2"/>
      <range lower="0.500000" upper="1.000000" label="0.5 to 1.0 (severe transit desert)" render="true" symbol="3"/>
    </ranges>
    <symbols>
      <symbol type="fill" name="0" alpha="1">
        <layer class="SimpleFill" enabled="1">
          <Option type="Map">
            <Option type="QString" name="color" value="43,140,190,255"/>
            <Option type="QString" name="outline_color" value="35,35,35,100"/>
            <Option type="QString" name="outline_width" value="0.1"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="1" alpha="1">
        <layer class="SimpleFill" enabled="1">
          <Option type="Map">
            <Option type="QString" name="color" value="166,219,160,255"/>
            <Option type="QString" name="outline_color" value="35,35,35,100"/>
            <Option type="QString" name="outline_width" value="0.1"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="2" alpha="1">
        <layer class="SimpleFill" enabled="1">
          <Option type="Map">
            <Option type="QString" name="color" value="253,174,97,255"/>
            <Option type="QString" name="outline_color" value="35,35,35,100"/>
            <Option type="QString" name="outline_width" value="0.1"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
      <symbol type="fill" name="3" alpha="1">
        <layer class="SimpleFill" enabled="1">
          <Option type="Map">
            <Option type="QString" name="color" value="215,25,28,255"/>
            <Option type="QString" name="outline_color" value="35,35,35,100"/>
            <Option type="QString" name="outline_width" value="0.1"/>
            <Option type="QString" name="style" value="solid"/>
          </Option>
        </layer>
      </symbol>
    </symbols>
  </renderer-v2>
</qgis>
