import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTranslation } from "../utils/i18n";
import api from "../services/api";
import ResponsiveDataTable from "../components/admin/ResponsiveDataTable";
import AdminMetricCard from "../components/admin/AdminMetricCard";
import AdminActionModal from "../components/admin/AdminActionModal";
import { useCurrency } from "../utils/currency";
import {
  ArrowPathIcon,
  BanknotesIcon,
  CalendarIcon,
  ChevronLeftIcon,
  CreditCardIcon,
  DocumentArrowDownIcon,
  DocumentMagnifyingGlassIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  PrinterIcon,
  UsersIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import * as XLSX from "xlsx";

export default function ReportsPage() {
  const { user } = useAuth();
  const { t } = useTranslation(user?.gym_id);
  const { formatCurrency, setCurrencyCode } = useCurrency(user?.gym_id);
  const [reports, setReports] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [dateRange, setDateRange] = useState({ start: "", end: "" });
  const [memberDetail, setMemberDetail] = useState(null);
  const [memberDetailLoading, setMemberDetailLoading] = useState(false);
  const [showMemberModal, setShowMemberModal] = useState(false);
  const [activeSection, setActiveSection] = useState("member");
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");
  const [filters, setFilters] = useState({
    memberId: "",
    paymentStatus: "All",
    paymentMethod: "All",
  });
  const [exportModal, setExportModal] = useState({
    isOpen: false,
    type: "members",
    format: "xlsx",
  });

  const fetchReports = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const params = new URLSearchParams();
      if (searchQuery.trim()) params.append("q", searchQuery.trim());
      if (dateRange.start) params.append("start_date", dateRange.start);
      if (dateRange.end) params.append("end_date", dateRange.end);
      if (filters.memberId) params.append("member_id", filters.memberId);
      if (filters.paymentStatus) params.append("status", filters.paymentStatus);
      if (filters.paymentMethod) params.append("method", filters.paymentMethod);
      params.append("page", String(page));
      params.append("per_page", String(perPage));
      params.append("sort_by", sortBy);
      params.append("sort_order", sortOrder);
      params.append("report_type", activeSection);

      const response = await api.get(`/api/reports?${params.toString()}`);
      setReports(response.data);
      if (response.data?.currency) {
        setCurrencyCode(response.data.currency);
      }
    } catch (err) {
      console.error("Failed to fetch reports:", err);
      setError(err.response?.data?.error || "Failed to load reports");
    } finally {
      setLoading(false);
    }
  }, [
    activeSection,
    dateRange.end,
    dateRange.start,
    filters.memberId,
    filters.paymentMethod,
    filters.paymentStatus,
    page,
    perPage,
    searchQuery,
    sortBy,
    sortOrder,
  ]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchReports();
    }, 250);

    return () => clearTimeout(timeoutId);
  }, [fetchReports]);

  const fetchMemberDetail = async (memberId) => {
    try {
      setMemberDetailLoading(true);
      const response = await api.get(`/api/reports/members/${memberId}`);
      setMemberDetail(response.data);
      if (response.data?.currency) {
        setCurrencyCode(response.data.currency);
      }
      setShowMemberModal(true);
    } catch (err) {
      console.error("Failed to fetch member report:", err);
      setError(err.response?.data?.error || "Failed to load member report");
    } finally {
      setMemberDetailLoading(false);
    }
  };

  const handleClearFilters = () => {
    setSearchQuery("");
    setDateRange({ start: "", end: "" });
    setFilters({ memberId: "", paymentStatus: "All", paymentMethod: "All" });
    setPage(1);
    setSortBy("created_at");
    setSortOrder("desc");
  };

  const formatDate = (value) => {
    if (!value) return "-";
    return new Date(value).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatDateTime = (value) => {
    if (!value) return "-";
    return new Date(value).toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatDuration = (minutes) => {
    if (minutes === null || minutes === undefined) return "-";
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return hours > 0
      ? `${hours}h ${remainingMinutes}m`
      : `${remainingMinutes}m`;
  };

  const exportData = async (type, format) => {
    const params = new URLSearchParams();
    if (searchQuery.trim()) params.append("q", searchQuery.trim());
    if (dateRange.start) params.append("start_date", dateRange.start);
    if (dateRange.end) params.append("end_date", dateRange.end);
    if (filters.memberId) params.append("member_id", filters.memberId);
    if (filters.paymentStatus) params.append("status", filters.paymentStatus);
    if (filters.paymentMethod) params.append("method", filters.paymentMethod);
    params.append("export", "1");

    const response = await api.get(`/api/reports?${params.toString()}`);
    const reportRows = getExportRowsFromPayload(type, response.data);
    if (!reportRows.length) return;

    // Format rows with user-friendly headers
    const formattedRows = reportRows.map(row => formatExportRow(row, type));
    const headers = getColumnHeaders(type);
    const headerKeys = Object.keys(formattedRows[0] || {});

    const baseName = `${type}-report`;
    
    if (format === "csv") {
      const csvRows = [];
      csvRows.push(headerKeys.join(","));
      formattedRows.forEach((row) => {
        csvRows.push(
          headerKeys.map((header) => {
            const value = row[header] ?? "";
            // Escape quotes and wrap in quotes if contains comma or quote
            const stringValue = String(value);
            if (stringValue.includes(",") || stringValue.includes('"') || stringValue.includes("\n")) {
              return `"${stringValue.replace(/"/g, '""')}"`;
            }
            return stringValue;
          }).join(",")
        );
      });

      const bom = "\uFEFF"; // UTF-8 BOM for Excel compatibility
      const blob = new Blob([bom + csvRows.join("\n")], {
        type: "text/csv;charset=utf-8;",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${baseName}.csv`;
      link.click();
      URL.revokeObjectURL(url);
      return;
    }

    if (format === "xlsx") {
      const worksheet = XLSX.utils.json_to_sheet(formattedRows);
      const workbook = XLSX.utils.book_new();
      
      // Auto-fit column widths
      const colWidths = headerKeys.map(key => ({
        wch: Math.max(key.length, ...formattedRows.map(row => String(row[key] || "").length)) + 2
      }));
      worksheet['!cols'] = colWidths;
      
      XLSX.utils.book_append_sheet(workbook, worksheet, "Report");
      XLSX.writeFile(workbook, `${baseName}.xlsx`);
      return;
    }

    if (format === "pdf") {
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      
      // Add page border
      doc.setDrawColor(200);
      doc.setLineWidth(0.5);
      doc.rect(5, 5, pageWidth - 10, pageHeight - 10);
      
      // Report title
      doc.setFontSize(18);
      doc.setFont("helvetica", "bold");
      doc.text(
        `${type.charAt(0).toUpperCase() + type.slice(1)} Report`,
        pageWidth / 2,
        20,
        { align: "center" }
      );
      
      // Report metadata
      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      doc.text(`Gym ID: ${user?.gym_id || "-"}`, 14, 30);
      doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 36);
      doc.text(`Total Records: ${formattedRows.length}`, 14, 42);
      
      // Prepare table data
      const tableData = formattedRows.map(row => headerKeys.map(key => row[key] || '-'));
      
      // Determine column alignment based on content
      const columnStyles = {};
      headerKeys.forEach((key, i) => {
        const sampleValue = String(formattedRows[0]?.[key] || '');
        // Check if the column contains numeric data (currency or numbers)
        const isNumeric = sampleValue.match(/^[\$€£]?\s*[\d,]+\.?\d*\s*[\$€£]?$/) || 
                         sampleValue.match(/^\d+$/) ||
                         key.toLowerCase().includes('amount') ||
                         key.toLowerCase().includes('paid') ||
                         key.toLowerCase().includes('revenue') ||
                         key.toLowerCase().includes('count');
        
        columnStyles[i] = {
          halign: isNumeric ? 'right' : 'left',
          cellPadding: 3,
          fontSize: 8,
        };
      });
      
      // Generate table with autoTable
      autoTable(doc, {
        startY: 50,
        head: [headerKeys],
        body: tableData,
        theme: 'grid',
        styles: {
          fontSize: 8,
          cellPadding: 3,
          overflow: 'linebreak',
        },
        headStyles: {
          fillColor: [243, 156, 18], // Orange background
          textColor: [255, 255, 255],
          fontStyle: 'bold',
          halign: 'center',
          cellPadding: 4,
          fontSize: 9,
        },
        alternateRowStyles: {
          fillColor: [249, 250, 251], // Light gray for alternating rows
        },
        columnStyles: columnStyles,
        margin: { top: 50, left: 14, right: 14, bottom: 20 },
        didDrawPage: function(data) {
          // Add page border on each page
          doc.setDrawColor(200);
          doc.setLineWidth(0.5);
          doc.rect(5, 5, pageWidth - 10, pageHeight - 10);
          
          // Add page number
          doc.setFontSize(8);
          doc.setFont("helvetica", "normal");
          doc.text(
            `Page ${doc.internal.getNumberOfPages()}`,
            pageWidth / 2,
            pageHeight - 10,
            { align: "center" }
          );
        },
      });
      
      doc.save(`${baseName}.pdf`);
    }
  };

  const printReport = () => {
    window.print();
  };

  const getExportRowsFromPayload = (type, payload) => {
    if (!payload) return [];
    if (type === "members") return payload.member_report?.members || [];
    if (type === "attendance")
      return payload.attendance_report?.attendance || [];
    if (type === "payments") return payload.payment_report?.payments || [];
    if (type === "revenue") return payload.revenue_report?.daily || [];
    return [];
  };

  const getColumnHeaders = (type) => {
    const headers = {
      members: {
        member_id: "Member ID",
        full_name: "Full Name",
        membership_plan_name: "Membership Plan",
        membership_start_date: "Join Date",
        membership_end_date: "Expiry Date",
        status: "Status",
        attendance_count: "Attendance Count",
        total_paid: "Total Paid",
        last_payment_date: "Last Payment Date",
        remaining_membership_days: "Remaining Days",
        phone: "Phone",
        email: "Email",
        gender: "Gender",
        date_of_birth: "Date of Birth",
        address: "Address",
        emergency_contact_name: "Emergency Contact Name",
        emergency_contact_phone: "Emergency Contact Phone",
      },
      attendance: {
        attendance_date: "Date",
        date: "Date",
        member_name: "Member Name",
        member_phone: "Member Phone",
        check_in_time: "Check In Time",
        check_out_time: "Check Out Time",
        duration_minutes: "Duration (Minutes)",
        status: "Status",
      },
      payments: {
        payment_date: "Payment Date",
        date: "Date",
        member_name: "Member Name",
        membership_plan_name: "Membership Plan",
        plan_name: "Plan Name",
        payment_amount: "Amount",
        amount: "Amount",
        payment_method: "Payment Method",
        method: "Method",
        payment_status: "Payment Status",
        status: "Status",
        transaction_id: "Transaction ID",
      },
      revenue: {
        date: "Date",
        revenue: "Revenue",
      },
    };
    return headers[type] || {};
  };

  const formatExportRow = (row, type) => {
    const headers = getColumnHeaders(type);
    const formattedRow = {};
    
    Object.keys(row).forEach(key => {
      if (headers[key]) {
        let value = row[key];
        // Format dates
        if (key.includes('date') || key.includes('_at')) {
          value = formatDate(value);
        }
        // Format currency
        if (key.includes('amount') || key.includes('paid') || key === 'revenue') {
          value = formatCurrency(value);
        }
        // Format duration
        if (key === 'duration_minutes') {
          value = formatDuration(value);
        }
        formattedRow[headers[key]] = value ?? '-';
      }
    });
    
    return formattedRow;
  };

  const summary = reports?.summary || {};

  const memberColumns = [
    { key: "member_id", label: "Member ID" },
    { key: "full_name", label: "Name" },
    { key: "membership_plan_name", label: "Plan" },
    {
      key: "membership_start_date",
      label: "Join Date",
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: "membership_end_date",
      label: "Expiry Date",
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: "status",
      label: "Status",
      render: (value) => (
        <span
          className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${value === "Active" ? "bg-green-50 text-green-700 border-green-200" : value === "Expired" ? "bg-red-50 text-red-700 border-red-200" : "bg-gray-50 text-gray-600 border-gray-200"}`}
        >
          {value || "-"}
        </span>
      ),
    },
    {
      key: "attendance_count",
      label: "Attendance",
      render: (value) => value ?? 0,
    },
    {
      key: "total_paid",
      label: "Total Paid",
      render: (value) => formatCurrency(value),
    },
    {
      key: "last_payment_date",
      label: "Last Payment",
      render: (value) => formatDate(value),
    },
    {
      key: "remaining_membership_days",
      label: "Remaining Days",
      render: (value) => (value === null || value === undefined ? "-" : value),
    },
  ];

  const attendanceColumns = [
    {
      key: "attendance_date",
      label: "Date",
      sortable: true,
      render: (value) => formatDate(value),
    },
    { key: "member_name", label: "Member" },
    { key: "member_phone", label: "Phone" },
    {
      key: "check_in_time",
      label: "Check In",
      render: (value) => formatDateTime(value),
    },
    {
      key: "check_out_time",
      label: "Check Out",
      render: (value) => (value ? formatDateTime(value) : "-"),
    },
    {
      key: "duration_minutes",
      label: "Duration",
      render: (value) => formatDuration(value),
    },
    {
      key: "status",
      label: "Status",
      render: (value) => (
        <span
          className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${value === "Checked Out" ? "bg-green-50 text-green-700 border-green-200" : "bg-orange-50 text-orange-700 border-orange-200"}`}
        >
          {value || "-"}
        </span>
      ),
    },
  ];

  const paymentColumns = [
    {
      key: "payment_date",
      label: "Date",
      sortable: true,
      render: (value) => formatDate(value),
    },
    { key: "member_name", label: "Member" },
    { key: "membership_plan_name", label: "Plan" },
    {
      key: "payment_amount",
      label: "Amount",
      render: (value) => formatCurrency(value),
    },
    { key: "payment_method", label: "Method" },
    {
      key: "payment_status",
      label: "Status",
      render: (value) => (
        <span
          className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${value === "Paid" ? "bg-green-50 text-green-700 border-green-200" : value === "Pending" ? "bg-yellow-50 text-yellow-700 border-yellow-200" : "bg-red-50 text-red-700 border-red-200"}`}
        >
          {value || "-"}
        </span>
      ),
    },
    { key: "transaction_id", label: "Transaction ID" },
  ];

  const revenueColumns = [
    { key: "date", label: "Date", render: (value) => formatDate(value) },
    {
      key: "revenue",
      label: "Revenue",
      render: (value) => formatCurrency(value),
    },
  ];

  const memberHistoryColumns = [
    {
      key: "attendance_date",
      label: "Date",
      render: (value) => formatDate(value),
    },
    {
      key: "check_in_time",
      label: "Check In",
      render: (value) => formatDateTime(value),
    },
    {
      key: "check_out_time",
      label: "Check Out",
      render: (value) => (value ? formatDateTime(value) : "-"),
    },
    {
      key: "duration_minutes",
      label: "Duration",
      render: (value) => formatDuration(value),
    },
    { key: "status", label: "Status" },
  ];

  const memberPaymentColumns = [
    {
      key: "payment_date",
      label: "Date",
      render: (value) => formatDate(value),
    },
    {
      key: "payment_amount",
      label: "Amount",
      render: (value) => formatCurrency(value),
    },
    { key: "payment_method", label: "Method" },
    { key: "payment_status", label: "Status" },
    { key: "transaction_id", label: "Transaction ID" },
  ];

  const attendanceMonthlyColumns = [
    { key: "date", label: "Date", render: (value) => formatDate(value) },
    { key: "checkins", label: "Check-ins" },
    { key: "checked_out", label: "Checked Out" },
  ];

  const selectedMember = reports?.member_report?.members?.find(
    (member) => String(member.id) === String(filters.memberId),
  );

  const handleMemberClick = (member) => {
    setFilters((prev) => ({ ...prev, memberId: String(member.id) }));
    fetchMemberDetail(member.id);
  };

  const renderSection = () => {
    if (activeSection === "member") {
      return (
        <section className="space-y-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-gray-900">{t('reports.membershipReport')}</h2>
              <p className="text-sm text-gray-600">
                Showing all members for the current gym
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() =>
                  setSortOrder((prev) => (prev === "asc" ? "desc" : "asc"))
                }
                className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-xl text-sm font-medium"
              >
                {t('common.filter')} {sortOrder.toUpperCase()}
              </button>
            </div>
          </div>
          <ResponsiveDataTable
            data={reports?.member_report?.members || []}
            columns={memberColumns}
            loading={loading}
            searchable={false}
            mobileCardLayout={true}
            onRowClick={handleMemberClick}
          />
          <div className="flex items-center justify-between gap-3">
            <p className="text-sm text-gray-600">
              {t('pagination.page')} {reports?.member_report?.page || 1} {t('pagination.of')}{' '}
              {reports?.member_report?.pages || 1}
            </p>
            <div className="flex gap-2">
              <button
                disabled={!reports?.member_report?.has_prev}
                onClick={() => setPage((prev) => Math.max(prev - 1, 1))}
                className="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
              >
                {t('pagination.previous')}
              </button>
              <button
                disabled={!reports?.member_report?.has_next}
                onClick={() => setPage((prev) => prev + 1)}
                className="px-4 py-2 rounded-xl bg-gray-100 hover:bg-gray-200 disabled:opacity-50"
              >
                {t('pagination.next')}
              </button>
            </div>
          </div>
        </section>
      );
    }

    if (activeSection === "attendance") {
      return (
        <section className="space-y-4">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                {t('reports.attendanceReport')}
              </h2>
              <p className="text-sm text-gray-600">
                Complete attendance history with member and date filters
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <select
                value={filters.memberId}
                onChange={(e) =>
                  setFilters((prev) => ({ ...prev, memberId: e.target.value }))
                }
                className="bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-sm"
              >
                <option value="">{t('members.title')}</option>
                {(reports?.member_report?.members || []).map((member) => (
                  <option key={member.id} value={member.id}>
                    {member.full_name}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <ResponsiveDataTable
            data={reports?.attendance_report?.attendance || []}
            columns={attendanceColumns}
            loading={loading}
            searchable={false}
            mobileCardLayout={true}
          />
          <div className="bg-white border border-gray-200 rounded-2xl p-4">
            <h3 className="font-semibold text-gray-900 mb-3">
              {t('attendance.monthlyAttendance')}
            </h3>
            <ResponsiveDataTable
              data={
                reports?.attendance_report?.monthly_summary?.daily_breakdown ||
                []
              }
              columns={attendanceMonthlyColumns}
              loading={loading}
              searchable={false}
              mobileCardLayout={true}
            />
          </div>
        </section>
      );
    }

    if (activeSection === "payments") {
      return (
        <section className="space-y-4">
          <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
            <div>
              <h2 className="text-lg font-bold text-gray-900">
                {t('reports.revenueReport')}
              </h2>
              <p className="text-sm text-gray-600">
                All payment records with status and method filters
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              <select
                value={filters.paymentStatus}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    paymentStatus: e.target.value,
                  }))
                }
                className="bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-sm"
              >
                <option value="All">{t('common.status')}</option>
                <option value="Paid">{t('payments.paid')}</option>
                <option value="Pending">{t('payments.unpaid')}</option>
                <option value="Failed">{t('payments.overdue')}</option>
              </select>
              <select
                value={filters.paymentMethod}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    paymentMethod: e.target.value,
                  }))
                }
                className="bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-sm"
              >
                <option value="All">{t('common.filter')}</option>
                <option value="Cash">{t('payments.cash')}</option>
                <option value="UPI">{t('payments.online')}</option>
                <option value="Card">{t('payments.card')}</option>
                <option value="Bank Transfer">{t('payments.bank')}</option>
              </select>
            </div>
          </div>
          <ResponsiveDataTable
            data={reports?.payment_report?.payments || []}
            columns={paymentColumns}
            loading={loading}
            searchable={false}
            mobileCardLayout={true}
          />
          <div className="bg-white border border-gray-200 rounded-2xl p-4 flex items-center justify-between">
            <span className="text-sm text-gray-600">{t('reports.totalAmount')}</span>
            <span className="font-bold text-gray-900">
              {formatCurrency(reports?.payment_report?.total_amount)}
            </span>
          </div>
        </section>
      );
    }

    return null;
  };

  const memberDetailData = memberDetail?.member;

  return (
    <div className="space-y-8 print:space-y-4">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-white border border-gray-200 rounded-2xl p-6 shadow-sm print:hidden">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <DocumentMagnifyingGlassIcon className="w-6 h-6 text-orange-500" />
            <h1 className="text-2xl font-bold text-gray-900">{t('reports.title')}</h1>
          </div>
          <p className="text-sm text-gray-600">
            Review tenant-scoped reports for Gym ID: {user?.gym_id}
          </p>
        </div>

        <div className="flex flex-wrap gap-3">
          <Link
            to="/dashboard"
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <ChevronLeftIcon className="w-4 h-4" /> {t('nav.dashboard')}
          </Link>
          <button
            onClick={() => fetchReports()}
            className="bg-orange-600 hover:bg-orange-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <ArrowPathIcon className="w-4 h-4" /> {t('common.refresh')}
          </button>
          <button
            onClick={printReport}
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <PrinterIcon className="w-4 h-4" /> {t('common.print')}
          </button>
          <button
            onClick={() =>
              setExportModal({
                isOpen: true,
                type:
                  activeSection === "attendance"
                    ? "attendance"
                    : activeSection === "payments"
                      ? "payments"
                      : activeSection === "revenue"
                        ? "revenue"
                        : "members",
                format: "xlsx",
              })
            }
            className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition-colors flex items-center gap-2"
          >
            <DocumentArrowDownIcon className="w-4 h-4" /> {t('common.export')}
          </button>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm print:hidden">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-5">
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
              {t('common.search')}
            </label>
            <div className="relative">
              <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                placeholder={t('reports.searchPlaceholder')}
                className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl pl-10 pr-4 py-3 text-sm text-gray-900 placeholder-gray-500 focus:outline-none transition-all duration-200"
              />
            </div>
          </div>
          <div className="lg:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
              {t('reports.fromDate')}
            </label>
            <input
              type="date"
              value={dateRange.start}
              onChange={(e) => {
                setDateRange((prev) => ({ ...prev, start: e.target.value }));
                setPage(1);
              }}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
            />
          </div>
          <div className="lg:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
              {t('reports.toDate')}
            </label>
            <input
              type="date"
              value={dateRange.end}
              onChange={(e) => {
                setDateRange((prev) => ({ ...prev, end: e.target.value }));
                setPage(1);
              }}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
            />
          </div>
          <div className="lg:col-span-2">
            <label className="block text-xs font-semibold uppercase tracking-wider text-gray-600 mb-2">
              {t('common.rowsPerPage')}
            </label>
            <select
              value={perPage}
              onChange={(e) => {
                setPerPage(Number(e.target.value));
                setPage(1);
              }}
              className="w-full bg-gray-50 border border-gray-200 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 rounded-xl px-4 py-3 text-sm text-gray-900 focus:outline-none transition-all duration-200"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
          <div className="lg:col-span-1 flex items-end">
            <button
              onClick={handleClearFilters}
              className="w-full bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-3 rounded-xl text-sm font-medium transition-colors flex items-center justify-center gap-2"
              title="Clear filters"
            >
              <XMarkIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm p-4 rounded-xl print:hidden">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-6 print:grid-cols-2 print:gap-4">
        <AdminMetricCard
          title={t('dashboard.totalMembers')}
          value={summary.total_members || 0}
          icon={<UsersIcon className="w-5 h-5" />}
          color="orange"
          loading={loading}
        />
        <AdminMetricCard
          title={t('attendance.title')}
          value={summary.total_attendance || 0}
          icon={<CalendarIcon className="w-5 h-5" />}
          color="blue"
          loading={loading}
        />
        <AdminMetricCard
          title={t('payments.title')}
          value={summary.total_payments || 0}
          icon={<CreditCardIcon className="w-5 h-5" />}
          color="green"
          loading={loading}
        />
        <AdminMetricCard
          title={t('reports.totalRevenue')}
          value={formatCurrency(summary.total_revenue)}
          icon={<BanknotesIcon className="w-5 h-5" />}
          color="red"
          loading={loading}
        />
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-4 shadow-sm print:hidden">
        <div className="flex flex-wrap gap-2">
          {[
            { key: "member", label: t('reports.membershipReport') },
            { key: "attendance", label: t('reports.attendanceReport') },
            { key: "payments", label: t('reports.revenueReport') },
          ].map((item) => (
            <button
              key={item.key}
              onClick={() => setActiveSection(item.key)}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${activeSection === item.key ? "bg-orange-600 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"}`}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {renderSection()}

      {selectedMember && (
        <div className="text-sm text-gray-600 print:hidden">
          Selected member: {selectedMember.full_name}
        </div>
      )}

      <AdminActionModal
        isOpen={showMemberModal}
        onClose={() => setShowMemberModal(false)}
        onConfirm={() => setShowMemberModal(false)}
        title={t('reports.membershipReport')}
        message={
          memberDetailData
            ? `${memberDetailData.full_name} detailed report`
            : t('common.loading')
        }
        confirmText={t('common.close')}
        type="info"
        loading={memberDetailLoading}
      >
        {memberDetailData && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-gray-500">{t('plans.title')}:</span>{" "}
                <span className="font-medium text-gray-900">
                  {memberDetailData.membership_plan || "-"}
                </span>
              </div>
              <div>
                <span className="text-gray-500">{t('members.joinDate')}:</span>{" "}
                <span className="font-medium text-gray-900">
                  {formatDate(memberDetail?.join_date)}
                </span>
              </div>
              <div>
                <span className="text-gray-500">{t('members.expiryDate')}:</span>{" "}
                <span className="font-medium text-gray-900">
                  {formatDate(memberDetail?.expiry_date)}
                </span>
              </div>
              <div>
                <span className="text-gray-500">{t('members.remainingDays')}:</span>{" "}
                <span className="font-medium text-gray-900">
                  {memberDetail?.remaining_membership_days ?? "-"}
                </span>
              </div>
              <div>
                <span className="text-gray-500">{t('attendance.title')}:</span>{" "}
                <span className="font-medium text-gray-900">
                  {memberDetail?.total_attendance ?? 0}
                </span>
              </div>
              <div>
                <span className="text-gray-500">{t('payments.totalPaid')}:</span>{" "}
                <span className="font-medium text-gray-900">
                  {formatCurrency(memberDetail?.total_amount_paid)}
                </span>
              </div>
              <div>
                <span className="text-gray-500">{t('payments.lastPayment')}:</span>{" "}
                <span className="font-medium text-gray-900">
                  {formatDate(memberDetail?.last_payment?.payment_date)}
                </span>
              </div>
              <div>
                <span className="text-gray-500">Status:</span>{" "}
                <span className="font-medium text-gray-900">
                  {memberDetail?.status || "-"}
                </span>
              </div>
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('attendance.attendanceHistory')}
              </h4>
              <ResponsiveDataTable
                data={memberDetail?.attendance_history || []}
                columns={memberHistoryColumns}
                loading={false}
                searchable={false}
                mobileCardLayout={true}
              />
            </div>
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">
                {t('payments.paymentHistory')}
              </h4>
              <ResponsiveDataTable
                data={memberDetail?.payment_history || []}
                columns={memberPaymentColumns}
                loading={false}
                searchable={false}
                mobileCardLayout={true}
              />
            </div>
          </div>
        )}
      </AdminActionModal>

      <AdminActionModal
        isOpen={exportModal.isOpen}
        onClose={() =>
          setExportModal({ isOpen: false, type: "members", format: "xlsx" })
        }
        onConfirm={() => {
          exportData(exportModal.type, exportModal.format);
          setExportModal({ isOpen: false, type: "members", format: "xlsx" });
        }}
        title="Export Report"
        message="Export the current report view using the active filters."
        confirmText={`Export ${exportModal.format.toUpperCase()}`}
        type="info"
      >
        <div className="space-y-3 text-sm text-gray-600">
          <p>Choose the report scope to export:</p>
          <div className="grid grid-cols-2 gap-2">
            {["members", "attendance", "payments", "revenue"].map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => setExportModal((prev) => ({ ...prev, type }))}
                className={`px-3 py-2 rounded-lg border text-sm ${exportModal.type === type ? "border-orange-500 text-orange-600 bg-orange-50" : "border-gray-200 text-gray-700 bg-white"}`}
              >
                {type}
              </button>
            ))}
          </div>
          <p className="pt-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
            Export format
          </p>
          <div className="grid grid-cols-3 gap-2">
            {[
              { key: "xlsx", label: "Excel" },
              { key: "csv", label: "CSV" },
              { key: "pdf", label: "PDF" },
            ].map((item) => (
              <button
                key={item.key}
                type="button"
                onClick={() =>
                  setExportModal((prev) => ({ ...prev, format: item.key }))
                }
                className={`px-3 py-2 rounded-lg border text-sm ${exportModal.format === item.key ? "border-orange-500 text-orange-600 bg-orange-50" : "border-gray-200 text-gray-700 bg-white"}`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>
      </AdminActionModal>
    </div>
  );
}
