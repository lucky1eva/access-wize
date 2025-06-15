import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Separator } from '@/components/ui/separator.jsx'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table.jsx'
import { Search, Download, FileText, Brain, Database, Loader2, AlertCircle, ExternalLink, Eye } from 'lucide-react'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import './App.css'

const API_BASE_URL = 'https://lnh8imcdj6dw.manus.space/api'

function App() {
  const [keyword, setKeyword] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [aiResponse, setAiResponse] = useState(null)
  const [pubmedResults, setPubmedResults] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerateStrategy = async () => {
    if (!keyword.trim()) return
    
    setIsGenerating(true)
    setError(null)
    
    try {
      // 第一步：生成Prompt
      const promptResponse = await fetch(`${API_BASE_URL}/generate_prompt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ keyword: keyword.trim() })
      })
      
      if (!promptResponse.ok) {
        throw new Error('生成Prompt失败')
      }
      
      const promptData = await promptResponse.json()
      
      // 第二步：调用AI生成策略
      const aiResponse = await fetch(`${API_BASE_URL}/get_ai_strategy`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: promptData.prompt })
      })
      
      if (!aiResponse.ok) {
        throw new Error('AI策略生成失败')
      }
      
      const aiData = await aiResponse.json()
      setAiResponse(aiData.ai_response)
      
    } catch (error) {
      console.error('生成检索策略失败:', error)
      setError(error.message || '生成检索策略时发生错误')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePubmedSearch = async () => {
    if (!aiResponse?.search_strategy) return
    
    setIsSearching(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_BASE_URL}/execute_pubmed_search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ search_strategy: aiResponse.search_strategy })
      })
      
      if (!response.ok) {
        throw new Error('PubMed检索失败')
      }
      
      const data = await response.json()
      setPubmedResults(data)
      
    } catch (error) {
      console.error('PubMed检索失败:', error)
      setError(error.message || 'PubMed检索时发生错误')
    } finally {
      setIsSearching(false)
    }
  }

  const downloadCSV = () => {
    if (!pubmedResults?.pubmed_results_csv) return
    
    try {
      // 解码base64 CSV数据
      const csvData = atob(pubmedResults.pubmed_results_csv)
      const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `pubmed_results_${keyword}_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('下载CSV文件失败:', error)
      setError('下载CSV文件时发生错误')
    }
  }

  const truncateText = (text, maxLength = 100) => {
    if (!text) return 'N/A'
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center py-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            专业文献检索工具
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            PubMed HTA检索策略生成器
          </p>
          <p className="text-sm text-gray-500">
            基于AI的卫生技术评估文献检索策略自动生成工具
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Input Section */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Search className="h-5 w-5" />
              关键词输入
            </CardTitle>
            <CardDescription>
              请输入您要检索的疾病、干预措施或其他关键词
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <Input
                placeholder="例如: insomnia, diabetes, hypertension..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="flex-1"
                onKeyPress={(e) => e.key === 'Enter' && handleGenerateStrategy()}
              />
              <Button 
                onClick={handleGenerateStrategy}
                disabled={!keyword.trim() || isGenerating}
                className="px-6"
              >
                {isGenerating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    生成中...
                  </>
                ) : (
                  <>
                    <Brain className="h-4 w-4 mr-2" />
                    生成检索策略
                  </>
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* AI Response Section */}
        {aiResponse && (
          <Card className="shadow-lg">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5" />
                AI生成的检索策略
              </CardTitle>
              <CardDescription>
                基于您的关键词生成的专业PubMed检索策略
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Search Strategy */}
              <div>
                <h3 className="font-semibold mb-2">检索策略</h3>
                <Textarea
                  value={aiResponse.search_strategy}
                  readOnly
                  className="min-h-[100px] font-mono text-sm"
                />
              </div>

              {/* Keywords Analysis */}
              <div>
                <h3 className="font-semibold mb-3">关键词分析</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  <div className="space-y-2">
                    <Badge variant="outline">疾病/病症</Badge>
                    <p className="text-sm text-gray-600">{aiResponse.keywords_analysis.disease}</p>
                  </div>
                  <div className="space-y-2">
                    <Badge variant="outline">干预措施</Badge>
                    <p className="text-sm text-gray-600">{aiResponse.keywords_analysis.intervention}</p>
                  </div>
                  <div className="space-y-2">
                    <Badge variant="outline">目标人群</Badge>
                    <p className="text-sm text-gray-600">{aiResponse.keywords_analysis.population}</p>
                  </div>
                  <div className="space-y-2">
                    <Badge variant="outline">研究类型</Badge>
                    <p className="text-sm text-gray-600">{aiResponse.keywords_analysis.study_type}</p>
                  </div>
                </div>
              </div>

              <Separator />

              {/* MeSH Terms */}
              <div>
                <h3 className="font-semibold mb-2">相关MeSH术语</h3>
                <div className="flex flex-wrap gap-2">
                  {aiResponse.mesh_terms.map((term, index) => (
                    <Badge key={index} variant="secondary">{term}</Badge>
                  ))}
                </div>
              </div>

              {/* Explanation and Tips */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                <div>
                  <h3 className="font-semibold mb-2">策略说明</h3>
                  <p className="text-sm text-gray-600">{aiResponse.explanation}</p>
                </div>
                <div>
                  <h3 className="font-semibold mb-2">检索建议</h3>
                  <p className="text-sm text-gray-600">{aiResponse.search_tips}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4">
                <div className="text-sm text-gray-500">
                  预估结果数量: {aiResponse.estimated_results}
                </div>
                <Button 
                  onClick={handlePubmedSearch}
                  disabled={isSearching}
                  className="px-6"
                >
                  {isSearching ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      检索中...
                    </>
                  ) : (
                    <>
                      <Database className="h-4 w-4 mr-2" />
                      执行PubMed检索
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* PubMed Results Section */}
        {pubmedResults && (
          <>
            {/* Results Summary */}
            <Card className="shadow-lg">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  PubMed检索结果
                </CardTitle>
                <CardDescription>
                  检索完成，共找到 {pubmedResults.total_count} 篇相关文献
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-green-600" />
                    <div>
                      <p className="font-medium text-green-800">检索完成</p>
                      <p className="text-sm text-green-600">
                        共检索到 {pubmedResults.total_count} 篇文献，已生成CSV文件
                      </p>
                    </div>
                  </div>
                  <Button onClick={downloadCSV} className="bg-green-600 hover:bg-green-700">
                    <Download className="h-4 w-4 mr-2" />
                    下载完整CSV文件
                  </Button>
                </div>
                
                <div className="text-sm text-gray-500 space-y-1">
                  <p>CSV文件包含以下字段：PMID、标题、作者、期刊、发表日期、DOI、摘要、研究类型等详细信息</p>
                  <p>检索时间：{new Date(pubmedResults.search_timestamp).toLocaleString('zh-CN')}</p>
                </div>
              </CardContent>
            </Card>

            {/* Preview Results */}
            {pubmedResults.preview_results && pubmedResults.preview_results.length > 0 && (
              <Card className="shadow-lg">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="h-5 w-5" />
                    文献预览（前10篇）
                  </CardTitle>
                  <CardDescription>
                    以下是检索结果的预览，完整结果请下载CSV文件
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-[80px]">PMID</TableHead>
                          <TableHead className="min-w-[300px]">标题</TableHead>
                          <TableHead className="w-[200px]">作者</TableHead>
                          <TableHead className="w-[200px]">期刊</TableHead>
                          <TableHead className="w-[120px]">发表日期</TableHead>
                          <TableHead className="w-[120px]">研究类型</TableHead>
                          <TableHead className="w-[80px]">链接</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {pubmedResults.preview_results.map((result, index) => (
                          <TableRow key={index}>
                            <TableCell className="font-mono text-sm">
                              {result.PMID}
                            </TableCell>
                            <TableCell>
                              <div className="max-w-[300px]">
                                <p className="text-sm font-medium leading-tight">
                                  {truncateText(result.Title, 150)}
                                </p>
                              </div>
                            </TableCell>
                            <TableCell>
                              <p className="text-sm text-gray-600">
                                {truncateText(result.Authors, 50)}
                              </p>
                            </TableCell>
                            <TableCell>
                              <p className="text-sm text-gray-600">
                                {truncateText(result.Journal, 50)}
                              </p>
                            </TableCell>
                            <TableCell>
                              <p className="text-sm text-gray-600">
                                {result.Publication_Date}
                              </p>
                            </TableCell>
                            <TableCell>
                              <Badge variant="outline" className="text-xs">
                                {result.Study_Type || 'N/A'}
                              </Badge>
                            </TableCell>
                            <TableCell>
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => window.open(result.URL, '_blank')}
                                className="h-8 w-8 p-0"
                              >
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                  
                  {pubmedResults.total_count > 10 && (
                    <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm text-blue-800">
                        <strong>注意：</strong>这里只显示前10篇文献的预览。
                        完整的 {pubmedResults.total_count} 篇文献信息请下载CSV文件查看。
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </>
        )}

        {/* Footer */}
        <div className="text-center py-6 text-sm text-gray-500">
          <p>专业文献检索工具 - 基于AI的PubMed HTA检索策略生成器</p>
          <p>支持OpenAI和DeepSeek大语言模型</p>
        </div>
      </div>
    </div>
  )
}

export default App

