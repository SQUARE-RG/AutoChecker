struct FloatHolder
{
    float value;

    void assign(double input)
    {
        value = static_cast<float>(input);
    }
};

int main()
{
    FloatHolder holder;
    holder.assign(2.5);
    return 0;
}
