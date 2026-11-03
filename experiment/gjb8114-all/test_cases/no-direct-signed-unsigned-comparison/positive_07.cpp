int main()
{
    int i = 0;
    unsigned int limit = 3;
    do
    {
        ++i;
    } while (static_cast<unsigned int>(i) != limit);
    return i;
}
