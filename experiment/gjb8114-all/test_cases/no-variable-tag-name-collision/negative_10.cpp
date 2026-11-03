template <typename T>
struct Box
{
    T value;
};

Box<int> makeBox(int value)
{
    return Box<int>{value};
}

int main()
{
    Box<int> Box = makeBox(3); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-4]
    int result = Box.value;
    return result;
}
