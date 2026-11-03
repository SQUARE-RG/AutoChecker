int main()
{
    int s = 1;
    unsigned int u = 3;
    int count = 0;
    for (; s < static_cast<int>(u); ++count) {
        s += 2;
    }
    return count;
}
