export interface Question {
  id: number;
  text: string;
  asked_by: string;
  created_at: string;
  answer_text: string | null;
  answered_by: string | null;
  answered_at: string | null;
}

export interface User {
  id: number;
  username: string;
  email: string;
  profile_picture: string | null;
  date_of_birth: string | null;
}

export interface Category {
  id: number;
  name: string;
  parent_id: number | null;
}

export interface CategoryGroup {
  id: number;
  name: string;
  children: Category[];
}

export interface ItemSummary {
  id: number;
  title: string;
  description: string;
  end_time: string;
  owner_username: string;
  starting_price: string;
  image: string | null;
  category_id: number | null;
  category_name: string | null;
  category_parent: string | null;
}

export interface UserBid {
  id: number;
  amount: string;
  created_at: string;
  item: ItemSummary;
}

export interface FavoriteItemResponse {
  items: ItemSummary[];
}

export interface Bid {
  id: number;
  amount: string;
  created_at: string;
  bidder_username: string;
  item_id: number;
  item_title: string;
  item_image: string | null;
}

export interface FavoriteBid {
  id: number;
  created_at: string;
  bid: Bid;
}

export interface LoginForm {
  username: string;
  password: string;
}

export interface SignupForm {
  username: string;
  email: string;
  password: string;
  passwordConfirm: string;
  date_of_birth: string;
  interests: number[];
}
