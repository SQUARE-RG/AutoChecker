enum class Shift : int
{
    kLeft = 1
};

int main()
{
    int value = 3;
    value = value << static_cast<int>(Shift::kLeft);
    return value;
}
