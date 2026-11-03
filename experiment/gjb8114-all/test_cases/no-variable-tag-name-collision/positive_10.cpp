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
    Box<int> boxed = makeBox(4);
    int result = boxed.value;
    return result;
}
