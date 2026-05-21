# AutoChecker

AutoChecker is a tool that automatically generates Java checkers for code checking tools with the support of LLM, taking rule text descriptions and rule test cases as input.

**Overview**:
![Overview](overview.png)



***Logic-guided API-Context Retrieval*** in overview:

![Logic-guided API-Context Retrieval](retrieval.png)

## What code checking tools can we generate checkers for currently?
AutoChecker can directly generate Java checkers for PMD, and is applicable to all code checking tools which support Java code checking based on AST traversal after making small adjustments.

## Tool Playground

We provide a tool demonstration website at https://autochecker.maskeduser.party.

## Repository Contents

### Directory  `tool`  -- Tool Implementation

+ `entity`: It stores data structures of three key entities(rule, test case and checker).
+ `retriever`: It stores semantic matcher and scripts for retrieving.
+ `utils`: It stores some intermediate data and auxiliary scripts.
+ `generator`: The source code of AutoChecker.
+ `main.py`: Entry of AutoChecker.

### Directory  `framework`  -- Something Useful of Code Checking Framework Where You Choose to Write Checker
Taking PMD framework as an example.
+ `pmd_db`: Content of two DBs(Full-API DB and Meta-API DB) constructed on PMD framework.
+ `pmd_project`: Source code of framework.
+ `PMD-Style-ASTParser.jar`: AST parser in code checking framework.

If you choose other code checking tools to generate checker, this information can also be quickly constructed (refer to our paper).

### Directory `experiment` -- Experimental Results
+ (Setup) experimental rules: `Experimental_20rules.json`.
+ (Setup) rules-related test case set: `experimental-20rules-test-suite`.
+ (RQ1) `baselines`: Results of baselines experiment.
+ (RQ1) `autochecker`: Results of AutoChecker evaluation experiment.
+ (RQ2) `ablation`: Results of ablation experiment.
+ (RQ4) `practice`: Detailed data about RQ4. 
  + Files ended with ".xml": Additionally added test cases in practice.
  + Files ended with ".txt": The augmented checker after iterating those added test cases.


## Detailed experimental results statistics(the best data marked in purple are taken in our paper)

<table>
  <tr>
    <th>Approach</th>
    <th>LLM</th>
    <th>#Rule<sub>pc</sub></th>
    <th>#Rule<sub>pot</sub></th>
    <th>#Rule<sub>pat</sub></th>
    <th>#TC<sub>pass</sub></th>
    <th>TPR<sub>avg</sub></th>
  </tr>
  <tr>
    <td rowspan="12">NoCaseLLM</td>
    <td rowspan="3">Llama3.1</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td rowspan="3">Qwen2.5-Coder</td>
    <td>5</td>
    <td>5</td>
    <td>1</td>
    <td>30</td>
    <td>17.82</td>
  </tr>
  <tr>
    <td>4</td>
    <td>3</td>
    <td>1</td>
    <td>30</td>
    <td>11.87</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>5</b></span></td>
    <td><span style="color: purple;"><b>5</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>40</b></span></td>
    <td><span style="color: purple;"><b>19.41</b></span></td>
  </tr>
<tr>
    <td rowspan="3">GPT-4</td>
    <td>4</td>
    <td>4</td>
    <td>0</td>
    <td>36</td>
    <td>15.57</td>
  </tr>
  <tr>
    <td>4</td>
    <td>4</td>
    <td>1</td>
    <td>37</td>
    <td>13.89</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>7</b></span></td>
    <td><span style="color: purple;"><b>7</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>62</b></span></td>
    <td><span style="color: purple;"><b>27.92</b></span></td>
  </tr>
<tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td>7</td>
    <td>7</td>
    <td>1</td>
    <td>42</td>
    <td>24.38</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>56</b></span></td>
    <td><span style="color: purple;"><b>28.06</b></span></td>
  </tr>
  <tr>
    <td>7</td>
    <td>7</td>
    <td>1</td>
    <td>54</td>
    <td>22.79</td>
  </tr>
  <tr>
    <td rowspan="12">AllCasesLLM</td>
    <td rowspan="3">Llama3.1</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td rowspan="3">Qwen2.5-Coder</td>
    <td>3</td>
    <td>3</td>
    <td>1</td>
    <td>14</td>
    <td>13.04</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>4</b></span></td>
    <td><span style="color: purple;"><b>4</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>17</b></span></td>
    <td><span style="color: purple;"><b>14.40</b></span></td>
  </tr>
  <tr>
    <td>3</td>
    <td>3</td>
    <td>1</td>
    <td>14</td>
    <td>13.04</td>
  </tr>
<tr>
    <td rowspan="3">GPT-4</td>
    <td>5</td>
    <td>5</td>
    <td>1</td>
    <td>38</td>
    <td>15.84</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>5</b></span></td>
    <td><span style="color: purple;"><b>5</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>36</b></span></td>
    <td><span style="color: purple;"><b>21.53</b></span></td>
  </tr>
  <tr>
    <td>6</td>
    <td>5</td>
    <td>2</td>
    <td>52</td>
    <td>19.40</td>
  </tr>
<tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td><span style="color: purple;"><b>6</b></span></td>
    <td><span style="color: purple;"><b>6</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>43</b></span></td>
    <td><span style="color: purple;"><b>24.60</b></span></td>
  </tr>
  <tr>
    <td>6</td>
    <td>6</td>
    <td>2</td>
    <td>50</td>
    <td>23.26</td>
  </tr>
  <tr>
    <td>5</td>
    <td>4</td>
    <td>2</td>
    <td>18</td>
    <td>15.89</td>
  </tr>
  <tr>
    <td rowspan="12">NoCaseLLM<sup>R</sup></td>
    <td rowspan="3">Llama3.1</td>
    <td>1</td>
    <td>1</td>
    <td>0</td>
    <td>1</td>
    <td>2.50</td>
  </tr>
  <tr>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>0</b></span></td>
    <td><span style="color: purple;"><b>16</b></span></td>
    <td><span style="color: purple;"><b>4.71</b></span></td>
  </tr>
  <tr>
    <td rowspan="3">Qwen2.5-Coder</td>
    <td>7</td>
    <td>7</td>
    <td>0</td>
    <td>43</td>
    <td>22.90</td>
  </tr>
  <tr>
    <td>8</td>
    <td>8</td>
    <td>1</td>
    <td>53</td>
    <td>27.76</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>60</b></span></td>
    <td><span style="color: purple;"><b>30.68</b></span></td>
  </tr>
<tr>
    <td rowspan="3">GPT-4</td>
    <td><span style="color: purple;"><b>10</b></span></td>
    <td><span style="color: purple;"><b>10</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>108</b></span></td>
    <td><span style="color: purple;"><b>30.82</b></span></td>
  </tr>
  <tr>
    <td>9</td>
    <td>9</td>
    <td>1</td>
    <td>92</td>
    <td>25.95</td>
  </tr>
  <tr>
    <td>6</td>
    <td>6</td>
    <td>1</td>
    <td>38</td>
    <td>22.73</td>
  </tr>
<tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>92</b></span></td>
    <td><span style="color: purple;"><b>32.05</b></span></td>
  </tr>
  <tr>
    <td>10</td>
    <td>9</td>
    <td>1</td>
    <td>94</td>
    <td>27.84</td>
  </tr>
  <tr>
    <td>10</td>
    <td>10</td>
    <td>1</td>
    <td>58</td>
    <td>27.60</td>
  </tr>
  <tr>
    <td rowspan="12">NoCaseLLM<sup>C</sup></td>
    <td rowspan="3">Llama3.1</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td rowspan="3">Qwen2.5-Coder</td>
    <td>5</td>
    <td>5</td>
    <td>1</td>
    <td>26</td>
    <td>15.74</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>6</b></span></td>
    <td><span style="color: purple;"><b>6</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>45</b></span></td>
    <td><span style="color: purple;"><b>21.18</b></span></td>
  </tr>
  <tr>
    <td>5</td>
    <td>5</td>
    <td>1</td>
    <td>30</td>
    <td>18.60</td>
  </tr>
<tr>
    <td rowspan="3">GPT-4</td>
    <td>7</td>
    <td>7</td>
    <td>0</td>
    <td>42</td>
    <td>22.19</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>94</b></span></td>
    <td><span style="color: purple;"><b>27.26</b></span></td>
  </tr>
  <tr>
    <td>8</td>
    <td>8</td>
    <td>1</td>
    <td>59</td>
    <td>22.86</td>
  </tr>
<tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>0</b></span></td>
    <td><span style="color: purple;"><b>66</b></span></td>
    <td><span style="color: purple;"><b>29.40</b></span></td>
  </tr>
  <tr>
    <td>8</td>
    <td>8</td>
    <td>1</td>
    <td>52</td>
    <td>28.71</td>
  </tr>
  <tr>
    <td>9</td>
    <td>9</td>
    <td>1</td>
    <td>105</td>
    <td>27.97</td>
  </tr>
  <tr>
    <td rowspan="12">NoCaseLLM<sup>RC</sup></td>
    <td rowspan="3">Llama3.1</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
    <td>0</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>0</b></span></td>
    <td><span style="color: purple;"><b>7</b></span></td>
    <td><span style="color: purple;"><b>6.25</b></span></td>
  </tr>
  <tr>
    <td>2</td>
    <td>2</td>
    <td>0</td>
    <td>8</td>
    <td>4.94</td>
  </tr>
  <tr>
    <td rowspan="3">Qwen2.5-Coder</td>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>9</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>60</b></span></td>
    <td><span style="color: purple;"><b>30.49</b></span></td>
  </tr>
  <tr>
    <td>8</td>
    <td>8</td>
    <td>1</td>
    <td>55</td>
    <td>27.09</td>
  </tr>
  <tr>
    <td>8</td>
    <td>7</td>
    <td>1</td>
    <td>41</td>
    <td>24.19</td>
  </tr>
<tr>
    <td rowspan="3">GPT-4</td>
    <td>8</td>
    <td>7</td>
    <td>1</td>
    <td>34</td>
    <td>22.87</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>105</b></span></td>
    <td><span style="color: purple;"><b>27.74</b></span></td>
  </tr>
  <tr>
    <td>8</td>
    <td>8</td>
    <td>0</td>
    <td>39</td>
    <td>22.50</td>
  </tr>
<tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td><span style="color: purple;"><b>11</b></span></td>
    <td><span style="color: purple;"><b>11</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>101</b></span></td>
    <td><span style="color: purple;"><b>38.93</b></span></td>
  </tr>
  <tr>
    <td>11</td>
    <td>11</td>
    <td>1</td>
    <td>119</td>
    <td>33.83</td>
  </tr>
  <tr>
    <td>11</td>
    <td>11</td>
    <td>1</td>
    <td>108</td>
    <td>32.09</td>
  </tr>
  <tr>
    <td rowspan="12">AutoChecker</td>
    <td rowspan="3">Llama3.1</td>
    <td><span style="color: purple;"><b>3</b></span></td>
    <td><span style="color: purple;"><b>3</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>22</b></span></td>
    <td><span style="color: purple;"><b>8.41</b></span></td>
  </tr>
  <tr>
    <td>2</td>
    <td>2</td>
    <td>0</td>
    <td>17</td>
    <td>4.12</td>
  </tr>
  <tr>
    <td>1</td>
    <td>1</td>
    <td>0</td>
    <td>17</td>
    <td>4.47</td>
  </tr>
  <tr>
    <td rowspan="3">Qwen2.5-Coder</td>
    <td><span style="color: purple;"><b>20</b></span></td>
    <td><span style="color: purple;"><b>20</b></span></td>
    <td><span style="color: purple;"><b>4</b></span></td>
    <td><span style="color: purple;"><b>257</b></span></td>
    <td><span style="color: purple;"><b>79.01</b></span></td>
  </tr>
  <tr>
    <td>18</td>
    <td>18</td>
    <td>3</td>
    <td>226</td>
    <td>65.62</td>
  </tr>
  <tr>
    <td>18</td>
    <td>18</td>
    <td>2</td>
    <td>241</td>
    <td>68.90</td>
  </tr>
<tr>
    <td rowspan="3">GPT-4</td>
    <td><span style="color: purple;"><b>20</b></span></td>
    <td><span style="color: purple;"><b>20</b></span></td>
    <td><span style="color: purple;"><b>6</b></span></td>
    <td><span style="color: purple;"><b>278</b></span></td>
    <td><span style="color: purple;"><b>82.28</b></span></td>
  </tr>
  <tr>
    <td>17</td>
    <td>17</td>
    <td>6</td>
    <td>228</td>
    <td>66.63</td>
  </tr>
  <tr>
    <td>20</td>
    <td>20</td>
    <td>5</td>
    <td>261</td>
    <td>79.36</td>
  </tr>
<tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td>18</td>
    <td>18</td>
    <td>5</td>
    <td>257</td>
    <td>76.59</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>19</b></span></td>
    <td><span style="color: purple;"><b>19</b></span></td>
    <td><span style="color: purple;"><b>4</b></span></td>
    <td><span style="color: purple;"><b>278</b></span></td>
    <td><span style="color: purple;"><b>80.86</b></span></td>
  </tr>
  <tr>
    <td>19</td>
    <td>19</td>
    <td>5</td>
    <td>264</td>
    <td>75.86</td>
  </tr>
  <tr>
    <td rowspan="6">AutoChecker<sup>WoR</sup></td>
    <td rowspan="3">GPT-4</td>
    <td>18</td>
    <td>18</td>
    <td>2</td>
    <td>230</td>
    <td>61.88</td>
  </tr>
  <tr>
    <td>15</td>
    <td>15</td>
    <td>3</td>
    <td>225</td>
    <td>56.38</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>18</b></span></td>
    <td><span style="color: purple;"><b>18</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>231</b></span></td>
    <td><span style="color: purple;"><b>67.27</b></span></td>
  </tr>
  <tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td><span style="color: purple;"><b>15</b></span></td>
    <td><span style="color: purple;"><b>15</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>221</b></span></td>
    <td><span style="color: purple;"><b>59.17</b></span></td>
  </tr>
  <tr>
    <td>14</td>
    <td>14</td>
    <td>2</td>
    <td>229</td>
    <td>58.03</td>
  </tr>
  <tr>
    <td>14</td>
    <td>14</td>
    <td>2</td>
    <td>210</td>
    <td>55.83</td>
  </tr>
  <tr>
    <td rowspan="6">AutoChecker<sup>WoI</sup></td>
    <td rowspan="3">GPT-4</td>
    <td>6</td>
    <td>6</td>
    <td>2</td>
    <td>31</td>
    <td>24.16</td>
  </tr>
  <tr>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>8</b></span></td>
    <td><span style="color: purple;"><b>2</b></span></td>
    <td><span style="color: purple;"><b>65</b></span></td>
    <td><span style="color: purple;"><b>29.37</b></span></td>
  </tr>
  <tr>
    <td>5</td>
    <td>5</td>
    <td>2</td>
    <td>33</td>
    <td>19.24</td>
  </tr>
  <tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td><span style="color: purple;"><b>14</b></span></td>
    <td><span style="color: purple;"><b>14</b></span></td>
    <td><span style="color: purple;"><b>4</b></span></td>
    <td><span style="color: purple;"><b>141</b></span></td>
    <td><span style="color: purple;"><b>53.44</b></span></td>
  </tr>
  <tr>
    <td>15</td>
    <td>15</td>
    <td>3</td>
    <td>162</td>
    <td>52.79</td>
  </tr>
  <tr>
    <td>13</td>
    <td>13</td>
    <td>3</td>
    <td>110</td>
    <td>42.96</td>
  </tr>
<tr>
    <td rowspan="6">AutoChecker<sup>WoM</sup></td>
    <td rowspan="3">GPT-4</td>
    <td><span style="color: purple;"><b>17</b></span></td>
    <td><span style="color: purple;"><b>17</b></span></td>
    <td><span style="color: purple;"><b>3</b></span></td>
    <td><span style="color: purple;"><b>256</b></span></td>
    <td><span style="color: purple;"><b>66.42</b></span></td>
  </tr>

<tr>
    <td>16</td>
    <td>16</td>
    <td>1</td>
    <td>189</td>
    <td>54.15</td>
  </tr>

<tr>
    <td>16</td>
    <td>16</td>
    <td>3</td>
    <td>239</td>
    <td>60.09</td>
  </tr>
  
  <tr>
    <td rowspan="3">DeepSeek-V3</td>
    <td><span style="color: purple;"><b>18</b></span></td>
    <td><span style="color: purple;"><b>18</b></span></td>
    <td><span style="color: purple;"><b>1</b></span></td>
    <td><span style="color: purple;"><b>258</b></span></td>
    <td><span style="color: purple;"><b>72.92</b></span></td>
  </tr>

<tr>
    <td>15</td>
    <td>15</td>
    <td>2</td>
    <td>215</td>
    <td>60.30</td>
  </tr>

<tr>
    <td>15</td>
    <td>15</td>
    <td>1</td>
    <td>209</td>
    <td>59.13</td>
  </tr>
  
</table>
