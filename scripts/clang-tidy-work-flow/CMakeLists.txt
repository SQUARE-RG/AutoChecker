set(LLVM_LINK_COMPONENTS
  support
  FrontendOpenMP
  )

add_clang_library(clangTidyUcasSaatModule
  HelloWorldCheck.cpp
  UcasSaatTidyModule.cpp

  LINK_LIBS
  clangTidy
  clangTidyCppCoreGuidelinesModule
  clangTidyUtils

  DEPENDS
  omp_gen
  )

clang_target_link_libraries(clangTidyUcasSaatModule
  PRIVATE
  clangAnalysis
  clangAnalysisFlowSensitive
  clangAnalysisFlowSensitiveModels
  clangAST
  clangASTMatchers
  clangBasic
  clangLex
  clangTooling
  clangTransformer
  )