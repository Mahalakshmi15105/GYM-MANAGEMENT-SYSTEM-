import { NavLink } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "../utils/i18n";
import GymLogo from "./GymLogo";
import {
  HomeIcon,
  GlobeAltIcon,
  BuildingOffice2Icon,
  CreditCardIcon,
  UserIcon,
  Cog6ToothIcon,
  NumberedListIcon,
  UsersIcon,
  CalendarIcon,
  HeartIcon,
  ChartBarIcon,
  ArrowRightOnRectangleIcon,
  XMarkIcon,
  ShieldCheckIcon,
} from "@heroicons/react/24/outline";

export default function Sidebar({ isOpen, setIsOpen }) {
  const { user, logout, isSuperAdmin, canAccessGymManagement } = useAuth();
  const { t } = useTranslation(user?.gym_id);

  // Base navigation links available to all users
  const baseLinks = [{ name: t('nav.dashboard'), path: "/dashboard", icon: HomeIcon }];

  // Super Admin specific navigation links
  const superAdminLinks = [
    {
      name: "Platform Dashboard",
      path: "/admin/dashboard",
      icon: GlobeAltIcon,
    },
    { name: "Gym Management", path: "/admin/gyms", icon: BuildingOffice2Icon },
    {
      name: "Subscriptions",
      path: "/admin/subscriptions",
      icon: CreditCardIcon,
    },
    { name: "User Management", path: "/admin/users", icon: UserIcon },
    { name: "System Settings", path: "/admin/settings", icon: Cog6ToothIcon },
    { name: "Activity Logs", path: "/admin/logs", icon: NumberedListIcon },
  ];

  // Gym management links for gym owners and super admins
  const gymManagementLinks = [
    { name: t('nav.members'), path: "/members", icon: UsersIcon },
    {
      name: t('nav.membershipPlans'),
      path: "/membership-plans",
      icon: CreditCardIcon,
    },
    { name: t('nav.payments'), path: "/payments", icon: CreditCardIcon },
    { name: t('nav.attendance'), path: "/attendance", icon: CalendarIcon },
    { name: t('nav.reports'), path: "/reports", icon: ChartBarIcon },
    { name: t('nav.trainersPlans'), path: "/plans", icon: HeartIcon },
    { name: t('nav.gymProfile'), path: "/gym-profile", icon: BuildingOffice2Icon },
    { name: t('nav.settings'), path: "/settings", icon: Cog6ToothIcon },
  ];

  // Build navigation links based on user role
  const getNavigationLinks = () => {
    let links = [...baseLinks];

    // Add Super Admin links first if user is super admin
    if (isSuperAdmin) {
      links = [...links, ...superAdminLinks];
    } else if (canAccessGymManagement) {
      // Add gym management links for gym owners
      links = [...links, ...gymManagementLinks];
    }

    return links;
  };

  const links = getNavigationLinks();

  return (
    <>
      {/* Mobile background overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-slate-950/60 backdrop-blur-sm z-40 lg:hidden transition-opacity duration-300"
          onClick={() => setIsOpen(false)}
        />
      )}

      <aside
        role="complementary"
        className={`w-64 bg-white border-r border-gray-200 flex flex-col h-screen fixed left-0 top-0 text-gray-800 z-50 transition-transform duration-300 shadow-lg ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0`}
      >
        {/* Brand logo & mobile close */}
        <div className="p-6 border-b border-gray-200 flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            {user ? (
              <>
                {!isSuperAdmin ? (
                  <GymLogo 
                    className="w-10 h-10" 
                    showGymName={true}
                    gymNameClassName="text-sm font-medium text-gray-900"
                  />
                ) : (
                  <div className="flex items-center gap-3">
                    <ShieldCheckIcon className="w-10 h-10 text-red-600" />
                    <div className="flex flex-col">
                      <span className="text-lg font-bold text-orange-500">
                        FlexiGym
                      </span>
                      <span className="text-xs text-gray-600 font-medium">
                        Platform Administration
                      </span>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <>
                <HeartIcon className="w-8 h-8 text-orange-600" />
                <span className="text-xl font-bold text-orange-500">
                  FlexiGym
                </span>
              </>
            )}
          </div>
          <button
            onClick={() => setIsOpen(false)}
            className="lg:hidden text-gray-400 hover:text-gray-600 p-1 focus:outline-none text-lg"
          >
            <XMarkIcon className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation menu */}
        <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
          {links.map((link, index) => {
            // Handle section dividers
            if (link.divider) {
              return (
                <div key={`divider-${index}`} className="py-2">
                  <div className="border-t border-gray-200 my-2"></div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-2">
                    {link.label}
                  </p>
                </div>
              );
            }

            // Regular navigation links
            const Icon = link.icon;
            return (
              <NavLink
                key={link.name}
                to={link.path}
                onClick={() => setIsOpen(false)} // Close sidebar on nav click on mobile
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? "bg-orange-500 text-white shadow-md"
                      : "hover:bg-orange-50 hover:text-orange-600"
                  }`
                }
              >
                <Icon className="w-5 h-5" />
                <span>{link.name}</span>
              </NavLink>
            );
          })}
        </nav>

        {/* Logged in User Profile area */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center gap-3 mb-4">
            <div
              className={`w-10 h-10 rounded-xl border flex items-center justify-center font-bold uppercase ${
                isSuperAdmin
                  ? "bg-red-100 border-red-200 text-red-600"
                  : "bg-orange-100 border-orange-200 text-orange-600"
              }`}
            >
              {user?.name?.charAt(0) || "U"}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">
                {user?.name}
              </p>
              <div className="flex items-center gap-1">
                <p className="text-xs text-gray-600 truncate capitalize">
                  {user?.role?.replace("_", " ")}
                </p>
                {isSuperAdmin && (
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 border border-red-200">
                    Admin
                  </span>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={logout}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold bg-gray-200 hover:bg-red-50 hover:text-red-600 border border-gray-200 hover:border-red-200 transition-all duration-200"
          >
            <ArrowRightOnRectangleIcon className="w-4 h-4" /> {t('nav.logout')}
          </button>
        </div>
      </aside>
    </>
  );
}
