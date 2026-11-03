struct Holder
{
    int value;
};

int main()
{
    Holder holder{0};
    holder.value = 45;
    return holder.value;
}
