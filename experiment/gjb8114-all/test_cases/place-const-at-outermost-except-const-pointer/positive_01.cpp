// 测试：指针声明中 const 位于类型说明最外层
int a = 42;

int main() {
    const int *p = &a;
    const int c = 7;
    return *p + c;
}
