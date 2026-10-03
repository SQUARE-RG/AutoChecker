import unittest
from autoql.quick_eval import *
from autoql.quick_eval.selectors import locate,resolve,protocol_position


class SelectorsTests(unittest.TestCase):
    def test_multiline_scopes_and_no_fake_declarations(self):
        text='''// predicate fake() {}
module Config {
  predicate isSource(
      int x,
      string s
  ) { x = 1 and s = "predicate fake() {}" }
  class Foo extends int {
    Foo() { this = 1 }
    string getName() { result = "hi" }
  }
}
/* class Fake extends int {} */
'''
        found=locate(text)
        self.assertEqual([(f['qualified_name'],f['arity']) for f in found],
            [('Config::isSource',2),('Config::Foo',None),('Config::Foo::Foo',0),('Config::Foo::getName',0)])

    def test_ambiguous_and_missing_snippet(self):
        for text,target,status in [('x x',SnippetTarget('x'),'ambiguous_target'),
                                    ('x',SnippetTarget('y'),'target_not_found')]:
            with self.assertRaises(QuickEvalError) as ctx: resolve(text,target)
            self.assertEqual(ctx.exception.status,status)

    def test_overload(self):
        text='predicate p(int x) {x=1}\npredicate p(string s) {s="x"}'
        with self.assertRaises(QuickEvalError) as ctx: resolve(text,SymbolTarget('p',1))
        self.assertEqual(ctx.exception.status,'ambiguous_target')

    def test_unicode_crlf(self):
        text='// 中文 😀\r\npredicate p() { 1=1 }\r\n'
        r,_=resolve(text,SnippetTarget('😀'))
        self.assertEqual(protocol_position(text,r,'x')['endColumn']-protocol_position(text,r,'x')['column'],2)
        r,_=resolve(text,SymbolTarget('p',0))
        self.assertEqual(protocol_position(text,r,'x')['line'],2)
        with self.assertRaises(QuickEvalError): protocol_position(text,SourceRange(1,1,1,1),'x')

    def test_parameterized_module_not_guessed(self):
        text='module M<T> { predicate p(int x) {x=1} }'
        with self.assertRaises(QuickEvalError) as ctx: resolve(text,SymbolTarget('M::p',1))
        self.assertEqual(ctx.exception.status,'unsupported_selector')

    def test_expression_not_mistaken_for_declaration(self):
        self.assertEqual(len(locate('predicate p(int x) { exists(int y | y=1 | x=y) }')),1)

    def test_known_cli_coordinate_compatibility(self):
        from autoql.quick_eval.protocol import position_encoding
        text='/*😀*/ x = 1'
        selected,_=resolve(text,SnippetTarget('x = 1'))
        self.assertEqual(position_encoding('2.23.3'),'codepoint')
        self.assertEqual(position_encoding('unknown'),'utf16')
        self.assertEqual(position_encoding('2.23.3','utf16'),'utf16')
        cp=protocol_position(text,selected,'x',position_encoding('2.23.3'))
        utf=protocol_position(text,selected,'x')
        self.assertEqual(cp['column']+1,utf['column'])
