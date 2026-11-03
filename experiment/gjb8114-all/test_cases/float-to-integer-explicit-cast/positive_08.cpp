int main()
{
    float base = 1.75f;
    int total = 0;
    for (int i = static_cast<int>(base); i < 4; ++i) {
        total += i;
    }
    return total;
}
