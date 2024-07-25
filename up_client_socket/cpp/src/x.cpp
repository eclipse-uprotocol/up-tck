#include <iostream>
#include <type_traits>
#include <optional>
#include <tuple>
#include <vector>
#include <array>

template <auto Start, auto End, auto Inc, class F>
constexpr void constexpr_for(F&& f)
{
    if constexpr (Start < End)
    {
        f(std::integral_constant<decltype(Start), Start>());
        constexpr_for<Start + Inc, End, Inc>(f);
    }
}

template <typename T>
std::ostream& operator<<(std::ostream& os, const std::optional<T>& arg)
{
	if (arg != std::nullopt) os << *arg;
	else os << "nullopt";
	return os;
}

template <class... Args>
std::ostream& operator<<(std::ostream& os, const std::tuple<Args...>& t)
{
    // const auto len = 4;
    const auto len = std::tuple_size_v< std::tuple<Args...> >;
	constexpr_for<0, len, 1>([&](auto i) {
        os << ' ' << std::get<i>(t);
    });
	return os;
}

using namespace std;

template <typename T>
void assign_if(T& field, size_t& cnt, size_t i, size_t bits)
{
}

template <typename T>
void assign_if(optional<T>& field, size_t& cnt, size_t i, size_t bits)
{
    if (((1<<i) & bits) && (field != nullopt)) {
        field = nullopt;
        cnt++;
    }
}

template <typename T>
vector<T> makeWildcardKeys(const T& key)
{
    const auto len = std::tuple_size_v<T>;
    vector<T> ret;
    ret.push_back(key);
    constexpr_for<1, (1<<len), 1>([&](const auto bits) {
        auto out = key;
        size_t cnt = 0;
        constexpr_for<0, len, 1>([&](const auto i) {
            assign_if(get<i>(out), cnt, i, bits);
        });
        if (cnt > 0) {
            ret.push_back(out);
        }
    });
    return ret;
}

using UUriKey = tuple<optional<string>, optional<uint32_t>, optional<uint32_t>, uint32_t >;

template<typename ... input_t>
using tuple_cat_t = decltype(std::tuple_cat(std::declval<input_t>()...));

using CallbackKey = tuple_cat_t<UUriKey, UUriKey>;

// using CallbackKey = tuple<
//     optional<string>,
//     optional<uint32_t>,
//     optional<uint32_t>,
//     optional<uint32_t>,
//     optional<string>,
//     optional<uint32_t>,
//     optional<uint32_t>,
//     optional<uint32_t>
// >;

int main(int argc, char *argv[])
{
    // optional<int> x;
    // int y;

    // cout << is_optional_v<decltype(x)> << endl;
    // cout << is_optional_v<decltype(y)> << endl;

    CallbackKey k{string{"hello"}, 1, 2, 3, string{"goodbye"}, 4, 5, 6};
    cout << k << endl;
    auto v = makeWildcardKeys(k);
    for (const auto& x : v) {
        cout << x << endl;
    }
}