int mode = 0;
extern "C" int set_mode(int value)
{
    mode = value;
    return mode;
}
int main()
{
    return set_mode(5);
}
